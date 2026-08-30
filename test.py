import os
import time
from playwright.sync_api import sync_playwright

def get_update_cookies(output_file="cookies.txt"):
    """
    Arka planda gizli tarayıcı açarak YouTube'dan güncel çerezleri toplar
    ve yt-dlp için Netscape formatında kaydeder.
    """
    print("[+] Tarayıcı otomasyonu başlatılıyor, YouTube çerezleri toplanıyor...")
    
    with sync_playwright() as p:
        # Gerçek kullanıcı gibi davranması için Chromium başlatıyoruz
        browser = p.chromium.launch(headless=True) # Arka planda gizli çalışması için headless=True
        
        # YouTube tespit mekanizmalarını taklit eden bir User-Agent tanımlıyoruz
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        # YouTube ana sayfasına veya robots.txt sayfasına gidiyoruz (Bot korumasını tetiklememek için)
        page.goto("https://www.youtube.com/robots.txt", wait_until="networkidle")
        time.sleep(3) # Sayfanın ve çerezlerin tamamen oturması için kısa bir bekleme
        
        # Playwright context yapısından tüm aktif çerezleri çekiyoruz
        playwright_cookies = context.cookies()
        
        # Çerezleri yt-dlp'nin anlayacağı Netscape Formatına dönüştürme işlemi
        netscape_lines = [
            "# Netscape HTTP Cookie File",
            "# http://haxx.se",
            "# This is a generated file!  Do not edit.",
            ""
        ]
        
        for c in playwright_cookies:
            # Eksik veya boş değerleri Netscape kurallarına göre dolduruyoruz
            domain = c.get('domain', '.youtube.com')
            include_subdomains = "TRUE" if domain.startswith('.') else "FALSE"
            path = c.get('path', '/')
            secure = "TRUE" if c.get('secure', False) else "FALSE"
            # Geçerlilik süresi (Eksikse 1 yıl sonrasına atanır)
            expires = str(int(c.get('expires', time.time() + 31536000)))
            name = c.get('name', '')
            value = c.get('value', '')
            
            # Netscape formatı sekmelerle (\t) ayrılmış 7 sütundan oluşur
            line = f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
            netscape_lines.append(line)
        
        # Dosyayı diske kaydediyoruz
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(netscape_lines))
            
        browser.close()
        print(f"[+] Çerezler başarıyla güncellendi ve '{output_file}' dosyasına yazıldı.")

# ---- KULLANIM ÖRNEĞİ ----
if __name__ == "__main__":
    import yt_dlp
    
    # 1. Adım: Çerezleri otomatik çek ve dosyaya yaz
    get_update_cookies("cookies.txt")
    
    # 2. Adım: Üretilen çerez dosyasını yt-dlp parametrelerine bağla
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'cookies': 'cookies.txt', # Fonksiyonun ürettiği dosyayı doğrudan buraya veriyoruz
    }
    
    # Test sorgusu
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info("https://youtube.com", download=False)
            print(f"[+] Başarılı! Video Başlığı: {info.get('title')}")
        except Exception as e:
            print(f"[-] Hata oluştu: {e}")
