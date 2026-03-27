package pro.noty.caption.service;

import pro.noty.caption.Config;

import java.awt.Desktop;
import java.net.URI;

public class BrowserOpener {

    public static void openLinks() {
        System.out.println("\n🌐 Opening links...");

        try {
            if (Desktop.isDesktopSupported()) {
                Desktop desktop = Desktop.getDesktop();

                // Open Telegram
                try {
                    desktop.browse(new URI(Config.TELEGRAM_LINK));
                    System.out.println("✓ Telegram opened");
                    Thread.sleep(1000);
                } catch (Exception e) {
                    System.err.println("⚠️ Could not open Telegram link: " + e.getMessage());
                }

                // Open YouTube
                try {
                    desktop.browse(new URI(Config.YOUTUBE_LINK));
                    System.out.println("✓ YouTube opened");
                } catch (Exception e) {
                    System.err.println("⚠️ Could not open YouTube link: " + e.getMessage());
                }
            } else {
                System.out.println("⚠️ Desktop not supported. Please manually visit:");
                System.out.println("Telegram: " + Config.TELEGRAM_LINK);
                System.out.println("YouTube: " + Config.YOUTUBE_LINK);
            }
        } catch (Exception e) {
            System.err.println("❌ Error opening browser: " + e.getMessage());
        }
    }
}