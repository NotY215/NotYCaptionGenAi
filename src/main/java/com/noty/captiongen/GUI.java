package com.noty.captiongen;

import javax.swing.*;
import javax.swing.border.*;
import javax.swing.plaf.basic.BasicButtonUI;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import java.io.*;
import java.nio.file.*;
import javax.swing.filechooser.FileNameExtensionFilter;

public class GUI extends JFrame {
    private JButton btnSelectFile;
    private JButton btnGenerate;
    private JButton btnDownloadModel;
    private JComboBox<String> modelCombo;
    private JLabel lblFileInfo;
    private JLabel lblStatus;
    private JSlider letterSpacingSlider;
    private JLabel lblLetterSpacingValue;
    private JComboBox<String> languageCombo;
    private JCheckBox chkTransliterate;
    private JLabel lblModelSize;
    private File selectedFile;
    private ModelDownloader modelDownloader;
    private boolean modelAvailable;
    private DownloadProgressDialog downloadDialog;
    private String selectedModelPath;
    private JPanel mainPanel;
    private Timer glowTimer;
    private float glowAlpha = 0.5f;
    private boolean glowing = false;

    // Professional Topaz-like colors
    private final Color DARK_BG = new Color(18, 18, 24);
    private final Color DARKER_BG = new Color(13, 13, 18);
    private final Color CARD_BG = new Color(28, 28, 35);
    private final Color LIGHT_TEXT = new Color(240, 240, 245);
    private final Color ACCENT_BLUE = new Color(64, 128, 255);
    private final Color ACCENT_GREEN = new Color(80, 200, 120);
    private final Color ACCENT_ORANGE = new Color(255, 160, 64);
    private final Color ACCENT_RED = new Color(255, 80, 80);
    private final Color ACCENT_PURPLE = new Color(160, 80, 255);
    private final Color GLOW_COLOR = new Color(64, 128, 255, 100);

    // Model information
    private static final class ModelInfo {
        String name;
        String url;
        String fileName;
        long sizeBytes;

        ModelInfo(String name, String url, String fileName, long sizeBytes) {
            this.name = name;
            this.url = url;
            this.fileName = fileName;
            this.sizeBytes = sizeBytes;
        }
    }

    private final ModelInfo[] MODELS = {
            new ModelInfo("Tiny (39 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
                    "ggml-tiny.bin", 39 * 1024 * 1024),
            new ModelInfo("Base (142 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
                    "ggml-base.bin", 142 * 1024 * 1024),
            new ModelInfo("Small (466 MB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
                    "ggml-small.bin", 466 * 1024 * 1024),
            new ModelInfo("Medium (1.5 GB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
                    "ggml-medium.bin", 1536 * 1024 * 1024),
            new ModelInfo("Large V1 (2.9 GB)",
                    "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v1.bin",
                    "ggml-large-v1.bin", 2900 * 1024 * 1024)
    };

    public GUI() {
        setTitle("NotYCaptionGenAi - AI Subtitle Generator");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(900, 800);
        setLocationRelativeTo(null);
        setUndecorated(true);

        // Set application icon
        try {
            ImageIcon icon = new ImageIcon(getClass().getResource("/app.ico"));
            setIconImage(icon.getImage());
            File iconFile = new File("app.ico");
            if (iconFile.exists()) {
                ImageIcon fileIcon = new ImageIcon(iconFile.getAbsolutePath());
                setIconImage(fileIcon.getImage());
            }
        } catch (Exception e) {
            System.err.println("Could not load icon: " + e.getMessage());
        }

        initComponents();
        checkModelStatus();

        // Setup window dragging
        setupWindowDragging();
    }

    private void initComponents() {
        setBackground(DARK_BG);

        // Main panel with gradient background
        mainPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                GradientPaint gp = new GradientPaint(0, 0, DARK_BG, getWidth(), getHeight(), DARKER_BG);
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, getWidth(), getHeight());
            }
        };
        mainPanel.setLayout(new BoxLayout(mainPanel, BoxLayout.Y_AXIS));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        mainPanel.setOpaque(false);

        // Custom Title Bar
        JPanel titleBar = createTitleBar();
        mainPanel.add(titleBar);

        // Title Panel
        JPanel titlePanel = createTitlePanel();
        mainPanel.add(titlePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));

        // File Selection Panel
        JPanel filePanel = createFilePanel();
        mainPanel.add(filePanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Model Selection Panel
        JPanel modelPanel = createModelPanel();
        mainPanel.add(modelPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Settings Panel
        JPanel settingsPanel = createSettingsPanel();
        mainPanel.add(settingsPanel);
        mainPanel.add(Box.createRigidArea(new Dimension(0, 20)));

        // Status Panel
        JPanel statusPanel = createStatusPanel();
        mainPanel.add(statusPanel);

        add(mainPanel);

        // Start glow animation
        startGlowAnimation();
    }

    private JPanel createTitleBar() {
        JPanel titleBar = new JPanel(new BorderLayout());
        titleBar.setBackground(new Color(13, 13, 18));
        titleBar.setBorder(BorderFactory.createEmptyBorder(10, 15, 10, 15));
        titleBar.setOpaque(true);

        JLabel titleLabel = new JLabel("NotYCaptionGenAi");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 16));
        titleLabel.setForeground(ACCENT_BLUE);

        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 5, 0));
        buttonPanel.setBackground(new Color(13, 13, 18));

        JButton minimizeBtn = createTitleButton("─");
        minimizeBtn.addActionListener(e -> setState(JFrame.ICONIFIED));

        JButton closeBtn = createTitleButton("✕");
        closeBtn.addActionListener(e -> System.exit(0));

        buttonPanel.add(minimizeBtn);
        buttonPanel.add(closeBtn);

        titleBar.add(titleLabel, BorderLayout.WEST);
        titleBar.add(buttonPanel, BorderLayout.EAST);

        return titleBar;
    }

    private JButton createTitleButton(String text) {
        JButton btn = new JButton(text);
        btn.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        btn.setForeground(LIGHT_TEXT);
        btn.setBackground(new Color(13, 13, 18));
        btn.setBorder(BorderFactory.createEmptyBorder(5, 10, 5, 10));
        btn.setFocusPainted(false);
        btn.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                btn.setBackground(new Color(40, 40, 50));
            }
            public void mouseExited(MouseEvent e) {
                btn.setBackground(new Color(13, 13, 18));
            }
        });
        return btn;
    }

    private JPanel createTitlePanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new BoxLayout(panel, BoxLayout.Y_AXIS));
        panel.setBackground(CARD_BG);
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(50, 50, 60), 1),
                BorderFactory.createEmptyBorder(25, 25, 25, 25)
        ));
        panel.setMaximumSize(new Dimension(860, 150));

        JLabel titleLabel = new JLabel("NotYCaptionGenAi");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 36));
        titleLabel.setForeground(ACCENT_BLUE);
        titleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(titleLabel);

        JLabel subtitleLabel = new JLabel("AI-Powered Subtitle Generator");
        subtitleLabel.setFont(new Font("Segoe UI", Font.PLAIN, 16));
        subtitleLabel.setForeground(LIGHT_TEXT);
        subtitleLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(subtitleLabel);

        JLabel creditLabel = new JLabel("Developed By NotY215 | LGPL v3 License");
        creditLabel.setFont(new Font("Segoe UI", Font.ITALIC, 11));
        creditLabel.setForeground(new Color(150, 150, 170));
        creditLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        panel.add(creditLabel);

        return panel;
    }

    private JPanel createFilePanel() {
        JPanel panel = new JPanel(new BorderLayout(10, 10));
        panel.setBackground(CARD_BG);
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(50, 50, 60), 1),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        panel.setMaximumSize(new Dimension(860, 100));

        btnSelectFile = createGlowButton("📁 Select Video/Audio File", ACCENT_BLUE);
        btnSelectFile.addActionListener(e -> selectFile());

        lblFileInfo = new JLabel("No file selected");
        lblFileInfo.setFont(new Font("Segoe UI", Font.ITALIC, 12));
        lblFileInfo.setForeground(new Color(150, 150, 170));
        lblFileInfo.setHorizontalAlignment(SwingConstants.CENTER);

        panel.add(btnSelectFile, BorderLayout.CENTER);
        panel.add(lblFileInfo, BorderLayout.SOUTH);

        return panel;
    }

    private JPanel createModelPanel() {
        JPanel panel = new JPanel(new GridBagLayout());
        panel.setBackground(CARD_BG);
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(50, 50, 60), 1),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        panel.setMaximumSize(new Dimension(860, 130));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(8, 10, 8, 10);

        gbc.gridx = 0;
        gbc.gridy = 0;
        JLabel modelLabel = new JLabel("Whisper Model:");
        modelLabel.setFont(new Font("Segoe UI", Font.BOLD, 13));
        modelLabel.setForeground(LIGHT_TEXT);
        panel.add(modelLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        String[] modelNames = new String[MODELS.length];
        for (int i = 0; i < MODELS.length; i++) {
            modelNames[i] = MODELS[i].name;
        }
        modelCombo = new JComboBox<>(modelNames);
        modelCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        modelCombo.setBackground(DARKER_BG);
        modelCombo.setForeground(LIGHT_TEXT);
        modelCombo.addActionListener(e -> updateModelInfo());
        panel.add(modelCombo, gbc);

        gbc.gridx = 0;
        gbc.gridy = 1;
        gbc.gridwidth = 1;
        JLabel sizeLabel = new JLabel("Model Size:");
        sizeLabel.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        sizeLabel.setForeground(LIGHT_TEXT);
        panel.add(sizeLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        lblModelSize = new JLabel("");
        lblModelSize.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lblModelSize.setForeground(ACCENT_GREEN);
        panel.add(lblModelSize, gbc);

        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        btnDownloadModel = createGlowButton("📥 Download Selected Model", ACCENT_ORANGE);
        btnDownloadModel.addActionListener(e -> confirmAndDownloadModel());
        panel.add(btnDownloadModel, gbc);

        return panel;
    }

    private JPanel createSettingsPanel() {
        JPanel panel = new JPanel();
        panel.setLayout(new GridBagLayout());
        panel.setBackground(CARD_BG);
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(50, 50, 60), 1),
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));
        panel.setMaximumSize(new Dimension(860, 230));

        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL;
        gbc.insets = new Insets(10, 10, 10, 10);

        // Letter Spacing
        gbc.gridx = 0;
        gbc.gridy = 0;
        JLabel letterSpacingLabel = new JLabel("Max Letters per Line:");
        letterSpacingLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        letterSpacingLabel.setForeground(LIGHT_TEXT);
        panel.add(letterSpacingLabel, gbc);

        gbc.gridx = 1;
        letterSpacingSlider = new JSlider(20, 80, 42);
        letterSpacingSlider.setMajorTickSpacing(10);
        letterSpacingSlider.setPaintTicks(true);
        letterSpacingSlider.setPaintLabels(true);
        letterSpacingSlider.setBackground(CARD_BG);
        letterSpacingSlider.setForeground(LIGHT_TEXT);
        panel.add(letterSpacingSlider, gbc);

        gbc.gridx = 2;
        lblLetterSpacingValue = new JLabel("42");
        lblLetterSpacingValue.setFont(new Font("Segoe UI", Font.BOLD, 14));
        lblLetterSpacingValue.setForeground(ACCENT_BLUE);
        panel.add(lblLetterSpacingValue, gbc);

        letterSpacingSlider.addChangeListener(e -> {
            lblLetterSpacingValue.setText(String.valueOf(letterSpacingSlider.getValue()));
        });

        // Language Selection
        gbc.gridx = 0;
        gbc.gridy = 1;
        JLabel languageLabel = new JLabel("Language:");
        languageLabel.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        languageLabel.setForeground(LIGHT_TEXT);
        panel.add(languageLabel, gbc);

        gbc.gridx = 1;
        gbc.gridwidth = 2;
        String[] languages = {"Auto Detect", "English", "Hindi", "Japanese", "Spanish", "French", "German", "Chinese", "Arabic", "Russian", "Korean"};
        languageCombo = new JComboBox<>(languages);
        languageCombo.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        languageCombo.setBackground(DARKER_BG);
        languageCombo.setForeground(LIGHT_TEXT);
        panel.add(languageCombo, gbc);

        // Transliteration Option
        gbc.gridx = 0;
        gbc.gridy = 2;
        gbc.gridwidth = 3;
        chkTransliterate = new JCheckBox("🔄 Transliterate to English (Hindi, Japanese, Arabic, Chinese, Korean, Russian)");
        chkTransliterate.setFont(new Font("Segoe UI", Font.PLAIN, 13));
        chkTransliterate.setBackground(CARD_BG);
        chkTransliterate.setForeground(LIGHT_TEXT);
        panel.add(chkTransliterate, gbc);

        // Generate Button
        gbc.gridx = 0;
        gbc.gridy = 3;
        gbc.gridwidth = 3;
        btnGenerate = createGlowButton("🚀 Generate Subtitles", ACCENT_GREEN);
        btnGenerate.setEnabled(false);
        btnGenerate.addActionListener(e -> confirmAndGenerate());
        panel.add(btnGenerate, gbc);

        return panel;
    }

    private JPanel createStatusPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(CARD_BG);
        panel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(50, 50, 60), 1),
                BorderFactory.createEmptyBorder(12, 15, 12, 15)
        ));
        panel.setMaximumSize(new Dimension(860, 80));

        lblStatus = new JLabel("✅ Ready. Select a file and model to begin.");
        lblStatus.setFont(new Font("Segoe UI", Font.PLAIN, 12));
        lblStatus.setForeground(ACCENT_GREEN);
        panel.add(lblStatus, BorderLayout.CENTER);

        return panel;
    }

    private JButton createGlowButton(String text, Color color) {
        JButton button = new JButton(text) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g.create();
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

                if (glowing && isEnabled()) {
                    g2d.setColor(new Color(color.getRed(), color.getGreen(), color.getBlue(), (int)(glowAlpha * 100)));
                    g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 12, 12);
                }

                super.paintComponent(g);
                g2d.dispose();
            }
        };

        button.setFont(new Font("Segoe UI", Font.BOLD, 13));
        button.setBackground(color);
        button.setForeground(Color.WHITE);
        button.setFocusPainted(false);
        button.setBorder(BorderFactory.createEmptyBorder(10, 20, 10, 20));
        button.setOpaque(true);

        button.addMouseListener(new MouseAdapter() {
            public void mouseEntered(MouseEvent e) {
                if (button.isEnabled()) {
                    button.setBackground(color.brighter());
                }
            }
            public void mouseExited(MouseEvent e) {
                if (button.isEnabled()) {
                    button.setBackground(color);
                }
            }
        });

        return button;
    }

    private void startGlowAnimation() {
        glowTimer = new Timer(50, e -> {
            if (glowing) {
                glowAlpha += 0.05f;
                if (glowAlpha > 1.0f) {
                    glowAlpha = 0.5f;
                }
                repaint();
            }
        });
        glowTimer.start();
    }

    private void setupWindowDragging() {
        Point[] mouseDrag = {null};
        addMouseListener(new MouseAdapter() {
            public void mousePressed(MouseEvent e) {
                mouseDrag[0] = e.getPoint();
            }
            public void mouseReleased(MouseEvent e) {
                mouseDrag[0] = null;
            }
        });
        addMouseMotionListener(new MouseMotionAdapter() {
            public void mouseDragged(MouseEvent e) {
                if (mouseDrag[0] != null) {
                    Point p = getLocation();
                    setLocation(p.x + e.getX() - mouseDrag[0].x, p.y + e.getY() - mouseDrag[0].y);
                }
            }
        });
    }

    private void updateModelInfo() {
        int index = modelCombo.getSelectedIndex();
        if (index >= 0 && index < MODELS.length) {
            long sizeMB = MODELS[index].sizeBytes / (1024 * 1024);
            lblModelSize.setText(String.format("%d MB", sizeMB));

            File modelFile = new File(MODELS[index].fileName);
            if (modelFile.exists() && modelFile.length() > 0) {
                modelAvailable = true;
                selectedModelPath = modelFile.getAbsolutePath();
                btnDownloadModel.setText("✓ Model Available");
                btnDownloadModel.setEnabled(false);
                btnGenerate.setEnabled(selectedFile != null);
                lblStatus.setText("✅ Model available. Ready to generate.");
                lblStatus.setForeground(ACCENT_GREEN);
            } else {
                modelAvailable = false;
                btnDownloadModel.setText("📥 Download Selected Model");
                btnDownloadModel.setEnabled(true);
                btnGenerate.setEnabled(false);
                lblStatus.setText("⚠️ Model not found. Please download it first.");
                lblStatus.setForeground(ACCENT_ORANGE);
            }
        }
    }

    private void selectFile() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Select Video or Audio File");

        String[] extensions = {"wav", "mp4", "mp3", "m4a", "mkv", "avi", "wmv", "mpeg", "flac"};
        FileNameExtensionFilter filter = new FileNameExtensionFilter(
                "Media Files (WAV, MP4, MP3, M4A, MKV, AVI, WMV, MPEG, FLAC)", extensions);
        fileChooser.setFileFilter(filter);

        int result = fileChooser.showOpenDialog(this);
        if (result == JFileChooser.APPROVE_OPTION) {
            selectedFile = fileChooser.getSelectedFile();
            lblFileInfo.setText(selectedFile.getName() + " (" + (selectedFile.length() / 1024 / 1024) + " MB)");

            if (modelAvailable) {
                btnGenerate.setEnabled(true);
                lblStatus.setText("✅ File selected. Ready to generate.");
            }
        }
    }

    private void confirmAndDownloadModel() {
        int index = modelCombo.getSelectedIndex();
        if (index < 0 || index >= MODELS.length) return;

        ModelInfo model = MODELS[index];
        long sizeMB = model.sizeBytes / (1024 * 1024);

        int response = JOptionPane.showConfirmDialog(this,
                String.format("Download %s (%d MB)?\n\nThis may take several minutes depending on your internet speed.",
                        model.name, sizeMB),
                "Confirm Download",
                JOptionPane.YES_NO_OPTION);

        if (response == JOptionPane.YES_OPTION) {
            downloadModel(model);
        }
    }

    private void confirmAndGenerate() {
        if (selectedFile == null) {
            JOptionPane.showMessageDialog(this, "Please select a file first!", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (!modelAvailable) {
            JOptionPane.showMessageDialog(this, "Whisper model not available. Please download it first!",
                    "Model Missing", JOptionPane.WARNING_MESSAGE);
            return;
        }

        int response = JOptionPane.showConfirmDialog(this,
                String.format("Generate subtitles for:\n%s\n\nModel: %s\nLanguage: %s\nMax letters: %d\nTransliteration: %s",
                        selectedFile.getName(),
                        MODELS[modelCombo.getSelectedIndex()].name,
                        languageCombo.getSelectedItem(),
                        letterSpacingSlider.getValue(),
                        chkTransliterate.isSelected() ? "Yes" : "No"),
                "Confirm Generation",
                JOptionPane.YES_NO_OPTION);

        if (response == JOptionPane.YES_OPTION) {
            generateSubtitles();
        }
    }

    private void downloadModel(ModelInfo model) {
        setButtonsEnabled(false);

        downloadDialog = new DownloadProgressDialog(this, model.name, model.sizeBytes);
        downloadDialog.setVisible(true);

        modelDownloader = new ModelDownloader();
        modelDownloader.downloadModel(model.url, model.fileName, model.sizeBytes, new ModelDownloader.DownloadCallback() {
            @Override
            public void onProgress(int percent, long downloaded, long total, double speed) {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null && !downloadDialog.isCancelled()) {
                        downloadDialog.updateProgress(percent, downloaded, total, speed);
                    }
                });
            }

            @Override
            public void onComplete(boolean success) {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null) {
                        downloadDialog.dispose();
                    }
                    setButtonsEnabled(true);

                    if (success) {
                        checkModelStatus();
                        JOptionPane.showMessageDialog(GUI.this,
                                "Model downloaded successfully!",
                                "Success", JOptionPane.INFORMATION_MESSAGE);
                    } else {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Failed to download model. Please check your internet connection.",
                                "Error", JOptionPane.ERROR_MESSAGE);
                    }
                });
            }

            @Override
            public void onCancel() {
                SwingUtilities.invokeLater(() -> {
                    if (downloadDialog != null) {
                        downloadDialog.dispose();
                    }
                    setButtonsEnabled(true);
                    lblStatus.setText("❌ Download cancelled.");
                    lblStatus.setForeground(ACCENT_RED);
                });
            }
        });
    }

    private void setButtonsEnabled(boolean enabled) {
        btnSelectFile.setEnabled(enabled);
        btnGenerate.setEnabled(enabled && modelAvailable && selectedFile != null);
        btnDownloadModel.setEnabled(enabled && !modelAvailable);
        modelCombo.setEnabled(enabled);
        languageCombo.setEnabled(enabled);
        letterSpacingSlider.setEnabled(enabled);
        chkTransliterate.setEnabled(enabled);

        glowing = enabled;
    }

    private void checkModelStatus() {
        int index = modelCombo.getSelectedIndex();
        if (index >= 0 && index < MODELS.length) {
            File modelFile = new File(MODELS[index].fileName);
            modelAvailable = modelFile.exists() && modelFile.length() > 0;

            if (modelAvailable) {
                selectedModelPath = modelFile.getAbsolutePath();
                btnDownloadModel.setText("✓ Model Available");
                btnDownloadModel.setEnabled(false);
                btnGenerate.setEnabled(selectedFile != null);
                lblStatus.setText("✅ Model available. Ready to generate.");
                lblStatus.setForeground(ACCENT_GREEN);
            } else {
                btnDownloadModel.setText("📥 Download Selected Model");
                btnDownloadModel.setEnabled(true);
                btnGenerate.setEnabled(false);
                lblStatus.setText("⚠️ Model not found. Please download it first.");
                lblStatus.setForeground(ACCENT_ORANGE);
            }
        }
    }

    private void generateSubtitles() {
        setButtonsEnabled(false);
        btnGenerate.setEnabled(false);

        lblStatus.setText("⏳ Processing... Extracting audio (if needed)...");
        lblStatus.setForeground(ACCENT_BLUE);

        SwingWorker<Void, String> worker = new SwingWorker<Void, String>() {
            private File tempAudioFile;

            @Override
            protected Void doInBackground() throws Exception {
                try {
                    publish("🎵 Extracting audio from media file...");
                    tempAudioFile = AudioExtractor.extractAudio(selectedFile);

                    publish("🎤 Transcribing with Whisper AI...");
                    String transcription = WhisperTranscriber.transcribe(tempAudioFile,
                            languageCombo.getSelectedItem().toString(),
                            selectedModelPath);

                    if (transcription == null || transcription.trim().isEmpty()) {
                        throw new Exception("Transcription failed - no text generated");
                    }

                    publish("📝 Generating SRT subtitles...");
                    int maxLetters = letterSpacingSlider.getValue();
                    String srtContent = SRTGenerator.generateSRT(transcription, maxLetters);

                    publish("💾 Saving subtitle file...");
                    String outputPath = selectedFile.getParent() + File.separator +
                            getFileNameWithoutExtension(selectedFile) + ".srt";
                    Files.write(Paths.get(outputPath), srtContent.getBytes());

                    if (chkTransliterate.isSelected()) {
                        publish("🔄 Performing transliteration...");
                        String transliterated = Transliterator.transliterate(srtContent);
                        String translitPath = selectedFile.getParent() + File.separator +
                                getFileNameWithoutExtension(selectedFile) + "_translit.srt";
                        Files.write(Paths.get(translitPath), transliterated.getBytes());
                        publish("✅ Transliterated version saved separately.");
                    }

                    publish("🎉 Subtitle generation completed successfully!");

                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Subtitles generated successfully!\n\nSaved to:\n" + outputPath +
                                        (chkTransliterate.isSelected() ? "\n\nTransliterated version also saved." : ""),
                                "Success", JOptionPane.INFORMATION_MESSAGE);
                    });

                } catch (Exception e) {
                    e.printStackTrace();
                    publish("❌ Error: " + e.getMessage());
                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(GUI.this,
                                "Error generating subtitles:\n" + e.getMessage(),
                                "Error", JOptionPane.ERROR_MESSAGE);
                    });
                } finally {
                    // Clean up temporary audio file
                    if (tempAudioFile != null && tempAudioFile.exists() &&
                            !selectedFile.getName().toLowerCase().endsWith(".wav")) {
                        try {
                            Thread.sleep(1000); // Wait for file to be released
                            tempAudioFile.delete();
                        } catch (Exception ex) {
                            System.err.println("Could not delete temp file: " + ex.getMessage());
                        }
                    }
                }
                return null;
            }

            @Override
            protected void process(java.util.List<String> chunks) {
                String lastMessage = chunks.get(chunks.size() - 1);
                lblStatus.setText(lastMessage);
            }

            @Override
            protected void done() {
                setButtonsEnabled(true);
                if (modelAvailable && selectedFile != null) {
                    btnGenerate.setEnabled(true);
                }
                lblStatus.setText("✅ Ready for next file.");
                lblStatus.setForeground(ACCENT_GREEN);
            }
        };

        worker.execute();
    }

    private String getFileNameWithoutExtension(File file) {
        String name = file.getName();
        int lastDot = name.lastIndexOf('.');
        if (lastDot > 0) {
            return name.substring(0, lastDot);
        }
        return name;
    }
}