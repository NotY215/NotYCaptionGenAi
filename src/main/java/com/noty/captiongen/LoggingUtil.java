package com.noty.captiongen;

import java.io.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.logging.*;

public class LoggingUtil {
    private static Logger logger = null;
    private static FileHandler fileHandler = null;
    private static String logFilePath = null;

    public static synchronized void initialize() {
        if (logger != null) return;

        try {
            // Create logs folder
            File logsDir = new File("logs");
            if (!logsDir.exists()) {
                logsDir.mkdirs();
            }

            // Create log file name with timestamp
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss");
            String timestamp = LocalDateTime.now().format(formatter);
            logFilePath = "logs/" + timestamp + ".log";

            // Configure logger
            logger = Logger.getLogger("NotYCaptionGenAi");
            logger.setUseParentHandlers(false);

            // Create file handler
            fileHandler = new FileHandler(logFilePath, true);
            fileHandler.setFormatter(new SimpleFormatter() {
                @Override
                public synchronized String format(LogRecord record) {
                    DateTimeFormatter dtf = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
                    String timestamp = LocalDateTime.now().format(dtf);
                    return String.format("[%s] [%s] %s%n",
                            timestamp,
                            record.getLevel().getName(),
                            record.getMessage());
                }
            });

            // Create console handler
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setFormatter(new SimpleFormatter() {
                @Override
                public synchronized String format(LogRecord record) {
                    return record.getMessage() + "\n";
                }
            });

            logger.addHandler(fileHandler);
            logger.addHandler(consoleHandler);
            logger.setLevel(Level.ALL);

            info("Logging initialized. Log file: " + logFilePath);

        } catch (Exception e) {
            System.err.println("Failed to initialize logger: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void log(String level, String message) {
        if (logger == null) {
            initialize();
        }

        switch (level.toUpperCase()) {
            case "INFO":
                logger.info(message);
                break;
            case "WARNING":
                logger.warning(message);
                break;
            case "SEVERE":
                logger.severe(message);
                break;
            case "FINE":
                logger.fine(message);
                break;
            default:
                logger.info(message);
        }
    }

    public static void info(String message) {
        log("INFO", message);
    }

    public static void warning(String message) {
        log("WARNING", message);
    }

    public static void error(String message) {
        log("SEVERE", message);
    }

    public static void error(String message, Exception e) {
        log("SEVERE", message + " - " + e.getMessage());
        if (e.getStackTrace() != null && e.getStackTrace().length > 0) {
            for (StackTraceElement element : e.getStackTrace()) {
                logger.severe("  at " + element.toString());
            }
        }
    }

    public static String getLogFilePath() {
        return logFilePath;
    }

    public static void close() {
        if (fileHandler != null) {
            fileHandler.close();
        }
    }
}