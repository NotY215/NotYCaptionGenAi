package pro.noty.caption.model;

import pro.noty.caption.Config;

public class CaptionConfig {
    private String mediaPath;
    private String modelPath;
    private String modelName;
    private String lineType;
    private int numberPerLine;
    private String outputPath;
    private int mode;
    private String modeName;
    private String languageCode;
    private String languageName;

    public CaptionConfig(String mediaPath, String modelPath, String modelName,
                         String lineType, int numberPerLine, int mode) {
        this(mediaPath, modelPath, modelName, lineType, numberPerLine, mode, "auto", "Auto Detect");
    }

    public CaptionConfig(String mediaPath, String modelPath, String modelName,
                         String lineType, int numberPerLine, int mode,
                         String languageCode, String languageName) {
        this.mediaPath = mediaPath;
        this.modelPath = modelPath;
        this.modelName = modelName;
        this.lineType = lineType;
        this.numberPerLine = numberPerLine;
        this.mode = mode;
        this.languageCode = languageCode;
        this.languageName = languageName;

        // Fix model path for large model
        if (modelName.equals("large")) {
            this.modelPath = modelPath.replace("large.bin", "large-v1.bin");
        }

        // Set mode name
        switch (mode) {
            case Config.MODE_NORMAL:
                this.modeName = "Normal (" + languageName + ")";
                break;
            case Config.MODE_TRANSLATION:
                this.modeName = "Translation to English";
                break;
            case Config.MODE_TRANSLITERATION:
                this.modeName = "Transliteration (Japanese/Hindi to English)";
                break;
            default:
                this.modeName = "Normal";
        }

        // Generate output path with mode suffix
        int lastDot = mediaPath.lastIndexOf('.');
        String baseName = mediaPath.substring(0, lastDot);
        String extension = mediaPath.substring(lastDot);

        String suffix = "";
        if (mode == Config.MODE_TRANSLATION) {
            suffix = "_en";
        } else if (mode == Config.MODE_TRANSLITERATION) {
            suffix = "_translit";
        } else if (!languageCode.equals("auto")) {
            suffix = "_" + languageCode;
        }

        this.outputPath = baseName + suffix + ".srt";
    }

    // Getters
    public String getMediaPath() { return mediaPath; }
    public String getModelPath() { return modelPath; }
    public String getModelName() { return modelName; }
    public String getLineType() { return lineType; }
    public int getNumberPerLine() { return numberPerLine; }
    public String getOutputPath() { return outputPath; }
    public int getMode() { return mode; }
    public String getModeName() { return modeName; }
    public String getLanguageCode() { return languageCode; }
    public String getLanguageName() { return languageName; }

    @Override
    public String toString() {
        return String.format(
                "\n📁 Media File: %s\n" +
                        "🤖 Model: %s\n" +
                        "🌐 Language: %s\n" +
                        "🎯 Subtitle Mode: %s\n" +
                        "📝 Line Type: %s\n" +
                        "🔢 %s per line: %d\n" +
                        "💾 Output: %s",
                mediaPath, modelName.toUpperCase(), languageName, modeName, lineType,
                lineType.substring(0, 1).toUpperCase() + lineType.substring(1),
                numberPerLine, outputPath
        );
    }
}