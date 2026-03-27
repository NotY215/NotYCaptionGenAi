package pro.noty.caption.service;

import pro.noty.caption.Config;
import pro.noty.caption.model.CaptionConfig;
import pro.noty.caption.util.ProgressBar;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.HashMap;

public class CaptionGenerator {

    // Simple transliteration maps for Japanese and Hindi
    private static final Map<String, String> JAPANESE_ROMAJI = new HashMap<>();
    private static final Map<String, String> HINDI_ROMAN = new HashMap<>();

    static {
        // Basic Japanese Hiragana to Romaji
        String[][] japaneseMap = {
                {"あ", "a"}, {"い", "i"}, {"う", "u"}, {"え", "e"}, {"お", "o"},
                {"か", "ka"}, {"き", "ki"}, {"く", "ku"}, {"け", "ke"}, {"こ", "ko"},
                {"さ", "sa"}, {"し", "shi"}, {"す", "su"}, {"せ", "se"}, {"そ", "so"},
                {"た", "ta"}, {"ち", "chi"}, {"つ", "tsu"}, {"て", "te"}, {"と", "to"},
                {"な", "na"}, {"に", "ni"}, {"ぬ", "nu"}, {"ね", "ne"}, {"の", "no"},
                {"は", "ha"}, {"ひ", "hi"}, {"ふ", "fu"}, {"へ", "he"}, {"ほ", "ho"},
                {"ま", "ma"}, {"み", "mi"}, {"む", "mu"}, {"め", "me"}, {"も", "mo"},
                {"や", "ya"}, {"ゆ", "yu"}, {"よ", "yo"},
                {"ら", "ra"}, {"り", "ri"}, {"る", "ru"}, {"れ", "re"}, {"ろ", "ro"},
                {"わ", "wa"}, {"を", "wo"}, {"ん", "n"}
        };

        for (String[] pair : japaneseMap) {
            JAPANESE_ROMAJI.put(pair[0], pair[1]);
        }

        // Basic Hindi to Romanized Hindi
        String[][] hindiMap = {
                {"अ", "a"}, {"आ", "aa"}, {"इ", "i"}, {"ई", "ee"}, {"उ", "u"}, {"ऊ", "oo"},
                {"ए", "e"}, {"ऐ", "ai"}, {"ओ", "o"}, {"औ", "au"},
                {"क", "ka"}, {"ख", "kha"}, {"ग", "ga"}, {"घ", "gha"}, {"ङ", "nga"},
                {"च", "cha"}, {"छ", "chha"}, {"ज", "ja"}, {"झ", "jha"}, {"ञ", "nya"},
                {"ट", "ta"}, {"ठ", "tha"}, {"ड", "da"}, {"ढ", "dha"}, {"ण", "na"},
                {"त", "ta"}, {"थ", "tha"}, {"द", "da"}, {"ध", "dha"}, {"न", "na"},
                {"प", "pa"}, {"फ", "pha"}, {"ब", "ba"}, {"भ", "bha"}, {"म", "ma"},
                {"य", "ya"}, {"र", "ra"}, {"ल", "la"}, {"व", "va"}, {"श", "sha"},
                {"ष", "sha"}, {"स", "sa"}, {"ह", "ha"}, {"क्ष", "ksha"}, {"त्र", "tra"},
                {"ज्ञ", "gya"}
        };

        for (String[] pair : hindiMap) {
            HINDI_ROMAN.put(pair[0], pair[1]);
        }
    }

    public boolean generateCaptions(CaptionConfig config) {
        System.out.println("\n🎬 Starting caption generation...");
        System.out.println("📝 This may take a while depending on media length...\n");

        try {
            // Build whisper command
            List<String> command = new ArrayList<>();
            command.add(Config.WHISPER_EXE_PATH);
            command.add("-m");
            command.add(config.getModelPath());
            command.add("-f");
            command.add(config.getMediaPath());

            // Set output file
            String outputPath = config.getOutputPath();
            command.add("-of");
            command.add(outputPath.substring(0, outputPath.lastIndexOf('.')));

            // Add common arguments
            command.add("-t");
            command.add("8"); // Threads
            command.add("-p");
            command.add("4"); // Processors

            // Add language options based on mode
            if (config.getMode() == Config.MODE_TRANSLATION) {
                command.add("-l");
                command.add("auto");
                command.add("-tr");
                command.add("en");
            } else if (config.getMode() == Config.MODE_TRANSLITERATION) {
                command.add("-l");
                command.add("auto");
            }

            // Output format
            command.add("--output-srt");

            // Print progress
            command.add("--print-progress");

            System.out.println("🔧 Running command: " + String.join(" ", command));

            // Execute whisper
            ProcessBuilder pb = new ProcessBuilder(command);
            pb.redirectErrorStream(true);
            Process process = pb.start();

            // Read output with progress simulation
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            String line;
            int progress = 0;

            while ((line = reader.readLine()) != null) {
                // Parse progress from whisper output
                if (line.contains("progress =")) {
                    try {
                        String progressStr = line.substring(line.indexOf("progress =") + 10);
                        progressStr = progressStr.trim().replace("%", "");
                        int percent = (int) Double.parseDouble(progressStr);
                        ProgressBar.showProgress(percent, 100);
                    } catch (Exception e) {
                        progress++;
                        ProgressBar.showProgress(progress % 100, 100);
                    }
                } else if (line.contains("Processing") || line.contains("Segment")) {
                    progress++;
                    ProgressBar.showProgress(progress % 100, 100);
                } else if (!line.isEmpty()) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor();

            if (exitCode == 0) {
                // Verify SRT file was created
                File srtFile = new File(config.getOutputPath());
                if (!srtFile.exists()) {
                    // Try alternative naming (whisper adds .srt automatically)
                    String altPath = config.getOutputPath().replace(".srt", "") + ".srt";
                    srtFile = new File(altPath);
                    if (srtFile.exists()) {
                        // Rename to our expected path
                        srtFile.renameTo(new File(config.getOutputPath()));
                    }
                }

                // Post-process based on mode
                if (config.getMode() == Config.MODE_TRANSLITERATION) {
                    transliterateSubtitles(config);
                } else {
                    postProcessSRT(config);
                }
                return true;
            } else {
                System.err.println("❌ Whisper process failed with exit code: " + exitCode);
                return false;
            }

        } catch (Exception e) {
            System.err.println("❌ Error generating captions: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }

    private void transliterateSubtitles(CaptionConfig config) throws IOException {
        File srtFile = new File(config.getOutputPath());
        if (!srtFile.exists()) {
            System.err.println("❌ SRT file not found: " + config.getOutputPath());
            return;
        }

        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(srtFile), "UTF-8"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        }

        // Process each line for transliteration
        List<String> processedLines = new ArrayList<>();
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            if (i % 4 == 2 && !line.trim().isEmpty()) { // Subtitle text line
                line = applyTransliteration(line);
                // Apply word/letter limit
                if (config.getLineType().equals("words")) {
                    line = limitWordsPerLine(line, config.getNumberPerLine());
                } else {
                    line = limitLettersPerLine(line, config.getNumberPerLine());
                }
            }
            processedLines.add(line);
        }

        // Write back with UTF-8 encoding
        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(srtFile), "UTF-8"))) {
            for (String line : processedLines) {
                writer.write(line);
                writer.newLine();
            }
        }

        System.out.println("\n✅ Captions generated with transliteration and saved to: " + config.getOutputPath());
    }

    private String applyTransliteration(String text) {
        // Detect if text contains Japanese or Hindi characters
        boolean hasJapanese = text.matches(".*[\\u3040-\\u309F\\u30A0-\\u30FF\\u4E00-\\u9FAF].*");
        boolean hasHindi = text.matches(".*[\\u0900-\\u097F].*");

        if (hasJapanese) {
            return transliterateJapanese(text);
        } else if (hasHindi) {
            return transliterateHindi(text);
        }

        return text; // Return as-is if no supported script detected
    }

    private String transliterateJapanese(String text) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            String ch = String.valueOf(text.charAt(i));
            String romaji = JAPANESE_ROMAJI.getOrDefault(ch, ch);
            result.append(romaji);
        }
        return result.toString();
    }

    private String transliterateHindi(String text) {
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < text.length(); i++) {
            String ch = String.valueOf(text.charAt(i));
            String roman = HINDI_ROMAN.getOrDefault(ch, ch);
            result.append(roman);
        }
        return result.toString();
    }

    private void postProcessSRT(CaptionConfig config) throws IOException {
        File srtFile = new File(config.getOutputPath());
        if (!srtFile.exists()) return;

        List<String> lines = new ArrayList<>();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(new FileInputStream(srtFile), "UTF-8"))) {
            String line;
            while ((line = reader.readLine()) != null) {
                lines.add(line);
            }
        }

        // Process based on preference
        List<String> processedLines = new ArrayList<>();
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            if (i % 4 == 2) { // Subtitle text line
                if (config.getLineType().equals("words")) {
                    line = limitWordsPerLine(line, config.getNumberPerLine());
                } else {
                    line = limitLettersPerLine(line, config.getNumberPerLine());
                }
            }
            processedLines.add(line);
        }

        // Write back with UTF-8 encoding
        try (BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(new FileOutputStream(srtFile), "UTF-8"))) {
            for (String line : processedLines) {
                writer.write(line);
                writer.newLine();
            }
        }

        System.out.println("\n✅ Captions generated and saved to: " + config.getOutputPath());
    }

    private String limitWordsPerLine(String text, int maxWords) {
        if (text == null || text.trim().isEmpty()) return text;
        String[] words = text.split("\\s+");
        if (words.length <= maxWords) return text;

        StringBuilder result = new StringBuilder();
        for (int i = 0; i < words.length; i++) {
            if (i > 0 && i % maxWords == 0) {
                result.append("\n");
            }
            result.append(words[i]);
            if (i < words.length - 1 && (i + 1) % maxWords != 0) {
                result.append(" ");
            }
        }
        return result.toString();
    }

    private String limitLettersPerLine(String text, int maxLetters) {
        if (text == null || text.trim().isEmpty()) return text;
        if (text.length() <= maxLetters) return text;

        StringBuilder result = new StringBuilder();
        int currentLength = 0;
        String[] words = text.split("\\s+");

        for (String word : words) {
            if (currentLength + word.length() + 1 > maxLetters && currentLength > 0) {
                result.append("\n");
                currentLength = 0;
            }
            if (currentLength > 0) {
                result.append(" ");
                currentLength++;
            }
            result.append(word);
            currentLength += word.length();
        }
        return result.toString();
    }
}