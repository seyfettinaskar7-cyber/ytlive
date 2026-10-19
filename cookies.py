from playwright.sync_api import sync_playwright

def get_update_cookies(output_file="cookies.txt"):
    """
    Arka planda gizli tarayıcı açarak YouTube'dan güncel çerezleri toplar
    ve yt-dlp için Netscape formatında kaydeder.
    """
    print("[+] Tarayıcı otomasyonu başlatılıyor, YouTube çerezleri toplanıyor...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.goto("https://www.youtube.com/robots.txt", wait_until="networkidle")
            time.sleep(8)  # Çerezlerin oturması için kısa bekleme

            playwright_cookies = context.cookies()
            netscape_lines = [
                "",
            ]

            for c in playwright_cookies:
                domain = c.get("domain", ".youtube.com")
                include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
                path = c.get("path", "/")
                secure = "TRUE" if c.get("secure", False) else "FALSE"
                expires = str(int(c.get("expires", time.time() + 31536000)))
                name = c.get("name", "")
                value = c.get("value", "")

                line = f"{domain}\t{include_subdomains}\t{path}\t{secure}\t{expires}\t{name}\t{value}"
                netscape_lines.append(line)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(netscape_lines))

            browser.close()
            print(f"[+] Çerezler başarıyla güncellendi: '{output_file}'")
    except Exception as e:
        print(f"⚠️ Çerez güncellenirken Playwright hatası oluştu: {e}")
