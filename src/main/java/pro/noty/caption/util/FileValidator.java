package pro.noty.caption.util;

import java.io.File;
import java.util.Arrays;

public class FileValidator {

    public static boolean validateMediaFile(String path, String[] allowedExtensions) {
        if (path == null || path.trim().isEmpty()) {
            return false;
        }

        File file = new File(path);
        if (!file.exists() || !file.isFile()) {
            return false;
        }

        if (!file.canRead()) {
            return false;
        }

        String fileName = file.getName();
        int lastDot = fileName.lastIndexOf('.');
        if (lastDot == -1) {
            return false;
        }

        String extension = fileName.substring(lastDot).toLowerCase();
        return Arrays.asList(allowedExtensions).contains(extension);
    }
}