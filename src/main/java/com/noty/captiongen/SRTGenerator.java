package com.noty.captiongen;

import java.util.*;
import java.util.regex.*;

public class SRTGenerator {

    public static String generateSRT(String transcription, int maxLettersPerLine) {
        List<SubtitleEntry> entries = parseTranscription(transcription);
        entries = applyLetterSpacing(entries, maxLettersPerLine);
        return generateSRTFormat(entries);
    }

    private static List<SubtitleEntry> parseTranscription(String transcription) {
        List<SubtitleEntry> entries = new ArrayList<>();

        Pattern pattern = Pattern.compile("(\\d+)\\n(\\d{2}:\\d{2}:\\d{2},\\d{3}) --> (\\d{2}:\\d{2}:\\d{2},\\d{3})\\n(.*?)(?:\\n\\n|$)",
                Pattern.DOTALL);
        Matcher matcher = pattern.matcher(transcription);

        while (matcher.find()) {
            SubtitleEntry entry = new SubtitleEntry();
            entry.index = Integer.parseInt(matcher.group(1));
            entry.startTime = matcher.group(2);
            entry.endTime = matcher.group(3);
            entry.text = matcher.group(4).trim();
            entries.add(entry);
        }

        return entries;
    }

    private static List<SubtitleEntry> applyLetterSpacing(List<SubtitleEntry> entries, int maxLetters) {
        List<SubtitleEntry> result = new ArrayList<>();

        for (SubtitleEntry entry : entries) {
            String[] words = entry.text.split(" ");
            StringBuilder currentLine = new StringBuilder();
            List<String> lines = new ArrayList<>();

            for (String word : words) {
                if (currentLine.length() + word.length() + 1 <= maxLetters) {
                    if (currentLine.length() > 0) {
                        currentLine.append(" ");
                    }
                    currentLine.append(word);
                } else {
                    if (currentLine.length() > 0) {
                        lines.add(currentLine.toString());
                    }
                    currentLine = new StringBuilder(word);
                }
            }

            if (currentLine.length() > 0) {
                lines.add(currentLine.toString());
            }

            if (lines.size() == 1) {
                entry.text = lines.get(0);
                result.add(entry);
            } else {
                long startMs = parseTimeToMs(entry.startTime);
                long endMs = parseTimeToMs(entry.endTime);
                long durationMs = endMs - startMs;
                long lineDurationMs = durationMs / lines.size();

                for (int i = 0; i < lines.size(); i++) {
                    SubtitleEntry newEntry = new SubtitleEntry();
                    newEntry.index = result.size() + 1;
                    long lineStartMs = startMs + (i * lineDurationMs);
                    long lineEndMs = lineStartMs + lineDurationMs;
                    newEntry.startTime = formatMsToTime(lineStartMs);
                    newEntry.endTime = formatMsToTime(lineEndMs);
                    newEntry.text = lines.get(i);
                    result.add(newEntry);
                }
            }
        }

        for (int i = 0; i < result.size(); i++) {
            result.get(i).index = i + 1;
        }

        return result;
    }

    private static String generateSRTFormat(List<SubtitleEntry> entries) {
        StringBuilder sb = new StringBuilder();

        for (SubtitleEntry entry : entries) {
            sb.append(entry.index).append("\n");
            sb.append(entry.startTime).append(" --> ").append(entry.endTime).append("\n");
            sb.append(entry.text).append("\n\n");
        }

        return sb.toString();
    }

    private static long parseTimeToMs(String time) {
        String[] parts = time.split("[:,]");
        int hours = Integer.parseInt(parts[0]);
        int minutes = Integer.parseInt(parts[1]);
        int seconds = Integer.parseInt(parts[2]);
        int millis = Integer.parseInt(parts[3]);

        return (hours * 3600000L) + (minutes * 60000L) + (seconds * 1000L) + millis;
    }

    private static String formatMsToTime(long ms) {
        long hours = ms / 3600000;
        ms %= 3600000;
        long minutes = ms / 60000;
        ms %= 60000;
        long seconds = ms / 1000;
        long millis = ms % 1000;

        return String.format("%02d:%02d:%02d,%03d", hours, minutes, seconds, millis);
    }

    private static class SubtitleEntry {
        int index;
        String startTime;
        String endTime;
        String text;
    }
}