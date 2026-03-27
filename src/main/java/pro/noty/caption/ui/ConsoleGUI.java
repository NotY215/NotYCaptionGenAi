package pro.noty.caption.ui;

import java.util.*;
import java.io.IOException;

public class ConsoleGUI {
    // ANSI color codes for better visuals
    public static final String RESET = "\u001B[0m";
    public static final String BLACK = "\u001B[30m";
    public static final String RED = "\u001B[31m";
    public static final String GREEN = "\u001B[32m";
    public static final String YELLOW = "\u001B[33m";
    public static final String BLUE = "\u001B[34m";
    public static final String PURPLE = "\u001B[35m";
    public static final String CYAN = "\u001B[36m";
    public static final String WHITE = "\u001B[37m";

    // Background colors
    public static final String BG_BLACK = "\u001B[40m";
    public static final String BG_RED = "\u001B[41m";
    public static final String BG_GREEN = "\u001B[42m";
    public static final String BG_YELLOW = "\u001B[43m";
    public static final String BG_BLUE = "\u001B[44m";
    public static final String BG_PURPLE = "\u001B[45m";
    public static final String BG_CYAN = "\u001B[46m";
    public static final String BG_WHITE = "\u001B[47m";

    // Text styles
    public static final String BOLD = "\u001B[1m";
    public static final String UNDERLINE = "\u001B[4m";
    public static final String BLINK = "\u001B[5m";

    private static final int BOX_WIDTH = 70;
    private static Scanner scanner = new Scanner(System.in);

    public static void clearScreen() {
        try {
            if (System.getProperty("os.name").contains("Windows")) {
                new ProcessBuilder("cmd", "/c", "cls").inheritIO().start().waitFor();
            } else {
                System.out.print("\033[H\033[2J");
                System.out.flush();
            }
        } catch (Exception e) {
            // Fallback: print blank lines
            for (int i = 0; i < 50; i++) {
                System.out.println();
            }
        }
    }

    public static void printHeader(String title) {
        System.out.println(CYAN + BOLD);
        System.out.println("╔" + repeatString("═", BOX_WIDTH - 2) + "╗");
        System.out.println("║" + centerText(title, BOX_WIDTH - 2) + "║");
        System.out.println("╚" + repeatString("═", BOX_WIDTH - 2) + "╝");
        System.out.println(RESET);
    }

    public static void printSubHeader(String title) {
        System.out.println(YELLOW + BOLD);
        System.out.println("┌" + repeatString("─", BOX_WIDTH - 2) + "┐");
        System.out.println("│" + centerText(title, BOX_WIDTH - 2) + "│");
        System.out.println("└" + repeatString("─", BOX_WIDTH - 2) + "┘");
        System.out.println(RESET);
    }

    public static void printBox(String... lines) {
        System.out.println(GREEN);
        System.out.println("┌" + repeatString("─", BOX_WIDTH - 2) + "┐");
        for (String line : lines) {
            System.out.println("│ " + padRight(line, BOX_WIDTH - 3) + "│");
        }
        System.out.println("└" + repeatString("─", BOX_WIDTH - 2) + "┘");
        System.out.println(RESET);
    }

    public static void printMenu(String title, String[] options, int selected) {
        System.out.println(CYAN + BOLD);
        System.out.println("┌" + repeatString("─", BOX_WIDTH - 2) + "┐");
        System.out.println("│ " + padRight(title, BOX_WIDTH - 3) + "│");
        System.out.println("├" + repeatString("─", BOX_WIDTH - 2) + "┤");

        for (int i = 0; i < options.length; i++) {
            String prefix = (i == selected) ? "▶ " : "  ";
            String suffix = (i == selected) ? " ◀" : "";
            String optionText = prefix + options[i] + suffix;
            System.out.println("│ " + padRight(optionText, BOX_WIDTH - 3) + "│");
        }

        System.out.println("└" + repeatString("─", BOX_WIDTH - 2) + "┘");
        System.out.println(RESET);
    }

    public static void printProgress(String title, int percent) {
        int barWidth = 50;
        int filled = (percent * barWidth) / 100;

        System.out.print(GREEN + title + ": ");
        System.out.print("[");
        for (int i = 0; i < barWidth; i++) {
            if (i < filled) {
                System.out.print("=");
            } else if (i == filled) {
                System.out.print(">");
            } else {
                System.out.print(" ");
            }
        }
        System.out.print("] " + percent + "%" + RESET);
        if (percent >= 100) {
            System.out.println();
        }
    }

    public static void printSuccess(String message) {
        System.out.println(GREEN + "✓ " + message + RESET);
    }

    public static void printError(String message) {
        System.out.println(RED + "✗ " + message + RESET);
    }

    public static void printWarning(String message) {
        System.out.println(YELLOW + "⚠ " + message + RESET);
    }

    public static void printInfo(String message) {
        System.out.println(CYAN + "ℹ " + message + RESET);
    }

    public static void printSeparator() {
        System.out.println(CYAN + repeatString("─", BOX_WIDTH) + RESET);
    }

    public static int showMenu(String title, String[] options) {
        int selected = 0;
        boolean running = true;

        while (running) {
            clearScreen();
            printHeader("NotY Caption Generator AI");
            printMenu(title, options, selected);
            System.out.println();
            System.out.println(YELLOW + "Use ↑/↓ arrows to navigate, Enter to select" + RESET);

            try {
                int input = getArrowKeyInput();
                if (input == -1) { // Enter
                    running = false;
                } else if (input == 1) { // Up
                    selected = (selected - 1 + options.length) % options.length;
                } else if (input == 2) { // Down
                    selected = (selected + 1) % options.length;
                }
            } catch (Exception e) {
                // Fallback to numeric input
                System.out.print("Enter option number (0-" + (options.length - 1) + "): ");
                try {
                    int choice = Integer.parseInt(scanner.nextLine());
                    if (choice >= 0 && choice < options.length) {
                        return choice;
                    }
                } catch (Exception ex) {
                    printError("Invalid input!");
                }
            }
        }

        return selected;
    }

    private static int getArrowKeyInput() throws IOException, InterruptedException {
        // Simple fallback - use numeric input
        // For proper arrow key support, you'd need a library like JLine
        // This is a simplified version
        System.out.print("➤ ");
        String input = scanner.nextLine();

        if (input.isEmpty()) {
            return -1; // Enter
        }

        // Simple numeric input
        try {
            int num = Integer.parseInt(input);
            if (num >= 0) {
                return num;
            }
        } catch (Exception e) {
            // Not a number
        }

        return -2; // No selection
    }

    public static String getInput(String prompt) {
        System.out.print(CYAN + prompt + RESET);
        return scanner.nextLine().trim();
    }

    public static String getInput(String prompt, String defaultValue) {
        System.out.print(CYAN + prompt + " [" + defaultValue + "]: " + RESET);
        String input = scanner.nextLine().trim();
        return input.isEmpty() ? defaultValue : input;
    }

    public static int getNumberInput(String prompt, int min, int max) {
        while (true) {
            System.out.print(CYAN + prompt + " (" + min + "-" + max + "): " + RESET);
            try {
                int value = Integer.parseInt(scanner.nextLine().trim());
                if (value >= min && value <= max) {
                    return value;
                }
                printError("Please enter a number between " + min + " and " + max);
            } catch (Exception e) {
                printError("Invalid number!");
            }
        }
    }

    public static boolean confirm(String prompt) {
        System.out.print(YELLOW + prompt + " (y/n): " + RESET);
        String input = scanner.nextLine().trim().toLowerCase();
        return input.equals("y") || input.equals("yes");
    }

    public static void pause() {
        System.out.print(YELLOW + "\nPress Enter to continue..." + RESET);
        scanner.nextLine();
    }

    public static void showLoading(String message) {
        System.out.print(CYAN + message + RESET);
        try {
            for (int i = 0; i < 3; i++) {
                Thread.sleep(500);
                System.out.print(".");
            }
            System.out.println();
        } catch (Exception e) {
            System.out.println();
        }
    }

    private static String repeatString(String str, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append(str);
        }
        return sb.toString();
    }

    private static String centerText(String text, int width) {
        if (text.length() >= width) return text.substring(0, width);
        int padding = (width - text.length()) / 2;
        return repeatString(" ", padding) + text + repeatString(" ", width - text.length() - padding);
    }

    private static String padRight(String text, int width) {
        if (text.length() >= width) return text.substring(0, width);
        return text + repeatString(" ", width - text.length());
    }
}