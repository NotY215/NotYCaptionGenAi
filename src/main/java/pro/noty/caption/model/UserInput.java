package pro.noty.caption.model;

public class UserInput {
    private String mediaPath;
    private String modelPath;
    private String modelName;
    private String preferenceType; // "words" or "letters"
    private int numberPerLine;

    public UserInput(String mediaPath, String modelPath, String modelName,
                     String preferenceType, int numberPerLine) {
        this.mediaPath = mediaPath;
        this.modelPath = modelPath;
        this.modelName = modelName;
        this.preferenceType = preferenceType;
        this.numberPerLine = numberPerLine;
    }

    // Getters and setters
    public String getMediaPath() { return mediaPath; }
    public void setMediaPath(String mediaPath) { this.mediaPath = mediaPath; }

    public String getModelPath() { return modelPath; }
    public void setModelPath(String modelPath) { this.modelPath = modelPath; }

    public String getModelName() { return modelName; }
    public void setModelName(String modelName) { this.modelName = modelName; }

    public String getPreferenceType() { return preferenceType; }
    public void setPreferenceType(String preferenceType) { this.preferenceType = preferenceType; }

    public int getNumberPerLine() { return numberPerLine; }
    public void setNumberPerLine(int numberPerLine) { this.numberPerLine = numberPerLine; }
}