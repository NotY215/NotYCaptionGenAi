package com.noty.captiongen;

import java.util.*;
import java.util.regex.*;

public class Transliterator {

    private static final Map<Character, String> HINDI_MAP = new HashMap<>();
    private static final Map<Character, String> JAPANESE_MAP = new HashMap<>();

    static {
        // Hindi Transliteration Map
        HINDI_MAP.put('अ', "a"); HINDI_MAP.put('आ', "aa"); HINDI_MAP.put('इ', "i");
        HINDI_MAP.put('ई', "ee"); HINDI_MAP.put('उ', "u"); HINDI_MAP.put('ऊ', "oo");
        HINDI_MAP.put('ए', "e"); HINDI_MAP.put('ऐ', "ai"); HINDI_MAP.put('ओ', "o");
        HINDI_MAP.put('औ', "au"); HINDI_MAP.put('क', "ka"); HINDI_MAP.put('ख', "kha");
        HINDI_MAP.put('ग', "ga"); HINDI_MAP.put('घ', "gha"); HINDI_MAP.put('च', "cha");
        HINDI_MAP.put('छ', "chha"); HINDI_MAP.put('ज', "ja"); HINDI_MAP.put('झ', "jha");
        HINDI_MAP.put('ट', "ta"); HINDI_MAP.put('ठ', "tha"); HINDI_MAP.put('ड', "da");
        HINDI_MAP.put('ढ', "dha"); HINDI_MAP.put('ण', "na"); HINDI_MAP.put('त', "ta");
        HINDI_MAP.put('थ', "tha"); HINDI_MAP.put('द', "da"); HINDI_MAP.put('ध', "dha");
        HINDI_MAP.put('न', "na"); HINDI_MAP.put('प', "pa"); HINDI_MAP.put('फ', "pha");
        HINDI_MAP.put('ब', "ba"); HINDI_MAP.put('भ', "bha"); HINDI_MAP.put('म', "ma");
        HINDI_MAP.put('य', "ya"); HINDI_MAP.put('र', "ra"); HINDI_MAP.put('ल', "la");
        HINDI_MAP.put('व', "va"); HINDI_MAP.put('श', "sha"); HINDI_MAP.put('ष', "sha");
        HINDI_MAP.put('स', "sa"); HINDI_MAP.put('ह', "ha"); HINDI_MAP.put('क्ष', "ksha");
        HINDI_MAP.put('त्र', "tra"); HINDI_MAP.put('ज्ञ', "gya");

        // Japanese basic Hiragana transliteration
        JAPANESE_MAP.put('あ', "a"); JAPANESE_MAP.put('い', "i"); JAPANESE_MAP.put('う', "u");
        JAPANESE_MAP.put('え', "e"); JAPANESE_MAP.put('お', "o"); JAPANESE_MAP.put('か', "ka");
        JAPANESE_MAP.put('き', "ki"); JAPANESE_MAP.put('く', "ku"); JAPANESE_MAP.put('け', "ke");
        JAPANESE_MAP.put('こ', "ko"); JAPANESE_MAP.put('さ', "sa"); JAPANESE_MAP.put('し', "shi");
        JAPANESE_MAP.put('す', "su"); JAPANESE_MAP.put('せ', "se"); JAPANESE_MAP.put('そ', "so");
        JAPANESE_MAP.put('た', "ta"); JAPANESE_MAP.put('ち', "chi"); JAPANESE_MAP.put('つ', "tsu");
        JAPANESE_MAP.put('て', "te"); JAPANESE_MAP.put('と', "to"); JAPANESE_MAP.put('な', "na");
        JAPANESE_MAP.put('に', "ni"); JAPANESE_MAP.put('ぬ', "nu"); JAPANESE_MAP.put('ね', "ne");
        JAPANESE_MAP.put('の', "no"); JAPANESE_MAP.put('は', "ha"); JAPANESE_MAP.put('ひ', "hi");
        JAPANESE_MAP.put('ふ', "fu"); JAPANESE_MAP.put('へ', "he"); JAPANESE_MAP.put('ほ', "ho");
        JAPANESE_MAP.put('ま', "ma"); JAPANESE_MAP.put('み', "mi"); JAPANESE_MAP.put('む', "mu");
        JAPANESE_MAP.put('め', "me"); JAPANESE_MAP.put('も', "mo"); JAPANESE_MAP.put('や', "ya");
        JAPANESE_MAP.put('ゆ', "yu"); JAPANESE_MAP.put('よ', "yo"); JAPANESE_MAP.put('ら', "ra");
        JAPANESE_MAP.put('り', "ri"); JAPANESE_MAP.put('る', "ru"); JAPANESE_MAP.put('れ', "re");
        JAPANESE_MAP.put('ろ', "ro"); JAPANESE_MAP.put('わ', "wa"); JAPANESE_MAP.put('を', "wo");
        JAPANESE_MAP.put('ん', "n");
    }

    public static String transliterate(String srtContent) {
        StringBuilder result = new StringBuilder();
        String[] lines = srtContent.split("\n");

        for (String line : lines) {
            // Check if line contains subtitle text (not timestamps or indices)
            if (!line.matches("\\d+") && !line.contains("-->") && !line.trim().isEmpty()) {
                String transliterated = transliterateText(line);
                result.append(transliterated);
            } else {
                result.append(line);
            }
            result.append("\n");
        }

        return result.toString();
    }

    private static String transliterateText(String text) {
        StringBuilder result = new StringBuilder();

        for (char c : text.toCharArray()) {
            // Check Hindi range
            if (c >= '\u0900' && c <= '\u097F') {
                result.append(HINDI_MAP.getOrDefault(c, String.valueOf(c)));
            }
            // Check Japanese Hiragana range
            else if (c >= '\u3040' && c <= '\u309F') {
                result.append(JAPANESE_MAP.getOrDefault(c, String.valueOf(c)));
            }
            // Check Japanese Katakana range
            else if (c >= '\u30A0' && c <= '\u30FF') {
                // Simple conversion for Katakana to Hiragana-like
                char hiragana = (char) (c - 0x60);
                result.append(JAPANESE_MAP.getOrDefault(hiragana, String.valueOf(c)));
            }
            else {
                result.append(c);
            }
        }

        return result.toString();
    }
}