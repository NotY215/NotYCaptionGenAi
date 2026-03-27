package pro.noty.caption.util;

public class ProgressBar {

    public static void showProgress(int current, int total) {
        if (total <= 0) return;

        int barLength = 50;
        double percent = (double) current / total;
        int filledLength = (int) (barLength * percent);

        StringBuilder bar = new StringBuilder("\r[");
        for (int i = 0; i < barLength; i++) {
            if (i < filledLength) {
                bar.append("=");
            } else if (i == filledLength) {
                bar.append(">");
            } else {
                bar.append(" ");
            }
        }
        bar.append("] ");

        String percentStr = String.format("%3d%%", current);
        bar.append(percentStr);

        System.out.print(bar.toString());

        if (current >= total) {
            System.out.println();
        }
    }

    public static void showProgress(long current, long total) {
        if (total <= 0) return;

        int barLength = 50;
        double percent = (double) current / total;
        int filledLength = (int) (barLength * percent);

        StringBuilder bar = new StringBuilder("\r[");
        for (int i = 0; i < barLength; i++) {
            if (i < filledLength) {
                bar.append("=");
            } else if (i == filledLength) {
                bar.append(">");
            } else {
                bar.append(" ");
            }
        }
        bar.append("] ");

        String percentStr = String.format("%.1f%%", percent * 100);
        bar.append(percentStr);

        String sizeStr = formatSize(current) + "/" + formatSize(total);
        bar.append(" ").append(sizeStr);

        System.out.print(bar.toString());

        if (current >= total) {
            System.out.println();
        }
    }

    private static String formatSize(long bytes) {
        if (bytes < 1024) return bytes + " B";
        int exp = (int) (Math.log(bytes) / Math.log(1024));
        String pre = "KMGTPE".charAt(exp - 1) + "";
        return String.format("%.1f %sB", bytes / Math.pow(1024, exp), pre);
    }
}