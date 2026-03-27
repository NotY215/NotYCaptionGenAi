package com.noty.captiongen;

import java.util.*;

public class Transliterator {

    public static String transliterate(String srtContent) {
        StringBuilder result = new StringBuilder();
        String[] lines = srtContent.split("\n");

        for (String line : lines) {
            if (!line.matches("\\d+") && !line.contains("-->") && !line.trim().isEmpty()) {
                result.append(transliterateText(line));
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
            // Hindi (Devanagari: U+0900 to U+097F)
            if (c >= '\u0900' && c <= '\u097F') {
                result.append(getHindiTransliteration(c));
            }
            // Japanese Hiragana (U+3040 to U+309F)
            else if (c >= '\u3040' && c <= '\u309F') {
                result.append(getJapaneseHiragana(c));
            }
            // Japanese Katakana (U+30A0 to U+30FF)
            else if (c >= '\u30A0' && c <= '\u30FF') {
                result.append(getJapaneseKatakana(c));
            }
            // Arabic (U+0600 to U+06FF)
            else if (c >= '\u0600' && c <= '\u06FF') {
                result.append(getArabicTransliteration(c));
            }
            // Korean Hangul (U+AC00 to U+D7AF)
            else if (c >= '\uAC00' && c <= '\uD7AF') {
                result.append(getKoreanTransliteration(c));
            }
            // Russian Cyrillic (U+0400 to U+04FF)
            else if (c >= '\u0400' && c <= '\u04FF') {
                result.append(getRussianTransliteration(c));
            }
            // Chinese (Simplified/Traditional) (U+4E00 to U+9FFF)
            else if (c >= '\u4E00' && c <= '\u9FFF') {
                result.append(getChinesePinyin(c));
            } else {
                result.append(c);
            }
        }

        return result.toString();
    }

    private static String getHindiTransliteration(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"अ","a"},{"आ","aa"},{"इ","i"},{"ई","ee"},{"उ","u"},{"ऊ","oo"},
                {"ए","e"},{"ऐ","ai"},{"ओ","o"},{"औ","au"},{"क","ka"},{"ख","kha"},
                {"ग","ga"},{"घ","gha"},{"च","cha"},{"छ","chha"},{"ज","ja"},{"झ","jha"},
                {"ट","ta"},{"ठ","tha"},{"ड","da"},{"ढ","dha"},{"ण","na"},{"त","ta"},
                {"थ","tha"},{"द","da"},{"ध","dha"},{"न","na"},{"प","pa"},{"फ","pha"},
                {"ब","ba"},{"भ","bha"},{"म","ma"},{"य","ya"},{"र","ra"},{"ल","la"},
                {"व","va"},{"श","sha"},{"ष","sha"},{"स","sa"},{"ह","ha"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getJapaneseHiragana(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"あ","a"},{"い","i"},{"う","u"},{"え","e"},{"お","o"},
                {"か","ka"},{"き","ki"},{"く","ku"},{"け","ke"},{"こ","ko"},
                {"さ","sa"},{"し","shi"},{"す","su"},{"せ","se"},{"そ","so"},
                {"た","ta"},{"ち","chi"},{"つ","tsu"},{"て","te"},{"と","to"},
                {"な","na"},{"に","ni"},{"ぬ","nu"},{"ね","ne"},{"の","no"},
                {"は","ha"},{"ひ","hi"},{"ふ","fu"},{"へ","he"},{"ほ","ho"},
                {"ま","ma"},{"み","mi"},{"む","mu"},{"め","me"},{"も","mo"},
                {"や","ya"},{"ゆ","yu"},{"よ","yo"},{"ら","ra"},{"り","ri"},
                {"る","ru"},{"れ","re"},{"ろ","ro"},{"わ","wa"},{"を","wo"},{"ん","n"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getJapaneseKatakana(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"ア","a"},{"イ","i"},{"ウ","u"},{"エ","e"},{"オ","o"},
                {"カ","ka"},{"キ","ki"},{"ク","ku"},{"ケ","ke"},{"コ","ko"},
                {"サ","sa"},{"シ","shi"},{"ス","su"},{"セ","se"},{"ソ","so"},
                {"タ","ta"},{"チ","chi"},{"ツ","tsu"},{"テ","te"},{"ト","to"},
                {"ナ","na"},{"ニ","ni"},{"ヌ","nu"},{"ネ","ne"},{"ノ","no"},
                {"ハ","ha"},{"ヒ","hi"},{"フ","fu"},{"ヘ","he"},{"ホ","ho"},
                {"マ","ma"},{"ミ","mi"},{"ム","mu"},{"メ","me"},{"モ","mo"},
                {"ヤ","ya"},{"ユ","yu"},{"ヨ","yo"},{"ラ","ra"},{"リ","ri"},
                {"ル","ru"},{"レ","re"},{"ロ","ro"},{"ワ","wa"},{"ヲ","wo"},{"ン","n"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getArabicTransliteration(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"ا","a"},{"ب","b"},{"ت","t"},{"ث","th"},{"ج","j"},{"ح","h"},
                {"خ","kh"},{"د","d"},{"ذ","dh"},{"ر","r"},{"ز","z"},{"س","s"},
                {"ش","sh"},{"ص","s"},{"ض","d"},{"ط","t"},{"ظ","z"},{"ع","'"},
                {"غ","gh"},{"ف","f"},{"ق","q"},{"ك","k"},{"ل","l"},{"م","m"},
                {"ن","n"},{"ه","h"},{"و","w"},{"ي","y"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getKoreanTransliteration(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"ㄱ","g"},{"ㄴ","n"},{"ㄷ","d"},{"ㄹ","r"},{"ㅁ","m"},{"ㅂ","b"},
                {"ㅅ","s"},{"ㅇ",""},{"ㅈ","j"},{"ㅊ","ch"},{"ㅋ","k"},{"ㅌ","t"},
                {"ㅍ","p"},{"ㅎ","h"},{"ㅏ","a"},{"ㅑ","ya"},{"ㅓ","eo"},{"ㅕ","yeo"},
                {"ㅗ","o"},{"ㅛ","yo"},{"ㅜ","u"},{"ㅠ","yu"},{"ㅡ","eu"},{"ㅣ","i"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getRussianTransliteration(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"а","a"},{"б","b"},{"в","v"},{"г","g"},{"д","d"},{"е","e"},
                {"ё","yo"},{"ж","zh"},{"з","z"},{"и","i"},{"й","y"},{"к","k"},
                {"л","l"},{"м","m"},{"н","n"},{"о","o"},{"п","p"},{"р","r"},
                {"с","s"},{"т","t"},{"у","u"},{"ф","f"},{"х","kh"},{"ц","ts"},
                {"ч","ch"},{"ш","sh"},{"щ","shch"},{"ъ",""},{"ы","y"},{"ь",""},
                {"э","e"},{"ю","yu"},{"я","ya"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }

    private static String getChinesePinyin(char c) {
        Map<Character, String> map = new HashMap<>();
        String[][] chars = {
                {"你","ni"},{"好","hao"},{"我","wo"},{"是","shi"},{"中","zhong"},
                {"国","guo"},{"人","ren"},{"们","men"},{"他","ta"},{"她","ta"},
                {"这","zhe"},{"那","na"},{"有","you"},{"在","zai"},{"不","bu"},
                {"了","le"},{"和","he"},{"对","dui"},{"吧","ba"},{"吗","ma"},
                {"啊","a"},{"哦","o"},{"嗯","en"},{"嗨","hai"},{"哈","ha"}
        };
        for (String[] p : chars) if (p[0].charAt(0) == c) return p[1];
        return String.valueOf(c);
    }
}