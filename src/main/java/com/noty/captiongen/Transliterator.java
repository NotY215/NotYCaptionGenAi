package com.noty.captiongen;

import java.util.*;

public class Transliterator {

    private static final Map<Character, String> HINDI_MAP = new HashMap<>();
    private static final Map<Character, String> JAPANESE_HIRAGANA_MAP = new HashMap<>();
    private static final Map<Character, String> JAPANESE_KATAKANA_MAP = new HashMap<>();
    private static final Map<Character, String> ARABIC_MAP = new HashMap<>();
    private static final Map<Character, String> CHINESE_PINYIN_MAP = new HashMap<>();
    private static final Map<Character, String> KOREAN_MAP = new HashMap<>();
    private static final Map<Character, String> RUSSIAN_MAP = new HashMap<>();

    static {
        // Hindi Transliteration Map (Devanagari)
        String[][] hindiChars = {
                {"अ","a"},{"आ","aa"},{"इ","i"},{"ई","ee"},{"उ","u"},{"ऊ","oo"},
                {"ए","e"},{"ऐ","ai"},{"ओ","o"},{"औ","au"},{"क","ka"},{"ख","kha"},
                {"ग","ga"},{"घ","gha"},{"च","cha"},{"छ","chha"},{"ज","ja"},{"झ","jha"},
                {"ट","ta"},{"ठ","tha"},{"ड","da"},{"ढ","dha"},{"ण","na"},{"त","ta"},
                {"थ","tha"},{"द","da"},{"ध","dha"},{"न","na"},{"प","pa"},{"फ","pha"},
                {"ब","ba"},{"भ","bha"},{"म","ma"},{"य","ya"},{"र","ra"},{"ल","la"},
                {"व","va"},{"श","sha"},{"ष","sha"},{"स","sa"},{"ह","ha"},{"क्ष","ksha"},
                {"त्र","tra"},{"ज्ञ","gya"},{"्",""},{"ा","aa"},{"ि","i"},{"ी","ee"},
                {"ु","u"},{"ू","oo"},{"े","e"},{"ै","ai"},{"ो","o"},{"ौ","au"}
        };

        for (String[] pair : hindiChars) {
            if (pair[0].length() == 1) {
                HINDI_MAP.put(pair[0].charAt(0), pair[1]);
            }
        }

        // Japanese Hiragana
        String[][] hiragana = {
                {"あ","a"},{"い","i"},{"う","u"},{"え","e"},{"お","o"},
                {"か","ka"},{"き","ki"},{"く","ku"},{"け","ke"},{"こ","ko"},
                {"さ","sa"},{"し","shi"},{"す","su"},{"せ","se"},{"そ","so"},
                {"た","ta"},{"ち","chi"},{"つ","tsu"},{"て","te"},{"と","to"},
                {"な","na"},{"に","ni"},{"ぬ","nu"},{"ね","ne"},{"の","no"},
                {"は","ha"},{"ひ","hi"},{"ふ","fu"},{"へ","he"},{"ほ","ho"},
                {"ま","ma"},{"み","mi"},{"む","mu"},{"め","me"},{"も","mo"},
                {"や","ya"},{"ゆ","yu"},{"よ","yo"},{"ら","ra"},{"り","ri"},
                {"る","ru"},{"れ","re"},{"ろ","ro"},{"わ","wa"},{"を","wo"},
                {"ん","n"},{"が","ga"},{"ぎ","gi"},{"ぐ","gu"},{"げ","ge"},
                {"ご","go"},{"ざ","za"},{"じ","ji"},{"ず","zu"},{"ぜ","ze"},
                {"ぞ","zo"},{"だ","da"},{"ぢ","ji"},{"づ","zu"},{"で","de"},
                {"ど","do"},{"ば","ba"},{"び","bi"},{"ぶ","bu"},{"べ","be"},
                {"ぼ","bo"},{"ぱ","pa"},{"ぴ","pi"},{"ぷ","pu"},{"ぺ","pe"},
                {"ぽ","po"}
        };

        for (String[] pair : hiragana) {
            JAPANESE_HIRAGANA_MAP.put(pair[0].charAt(0), pair[1]);
        }

        // Japanese Katakana
        String[][] katakana = {
                {"ア","a"},{"イ","i"},{"ウ","u"},{"エ","e"},{"オ","o"},
                {"カ","ka"},{"キ","ki"},{"ク","ku"},{"ケ","ke"},{"コ","ko"},
                {"サ","sa"},{"シ","shi"},{"ス","su"},{"セ","se"},{"ソ","so"},
                {"タ","ta"},{"チ","chi"},{"ツ","tsu"},{"テ","te"},{"ト","to"},
                {"ナ","na"},{"ニ","ni"},{"ヌ","nu"},{"ネ","ne"},{"ノ","no"},
                {"ハ","ha"},{"ヒ","hi"},{"フ","fu"},{"ヘ","he"},{"ホ","ho"},
                {"マ","ma"},{"ミ","mi"},{"ム","mu"},{"メ","me"},{"モ","mo"},
                {"ヤ","ya"},{"ユ","yu"},{"ヨ","yo"},{"ラ","ra"},{"リ","ri"},
                {"ル","ru"},{"レ","re"},{"ロ","ro"},{"ワ","wa"},{"ヲ","wo"},
                {"ン","n"},{"ガ","ga"},{"ギ","gi"},{"グ","gu"},{"ゲ","ge"},
                {"ゴ","go"},{"ザ","za"},{"ジ","ji"},{"ズ","zu"},{"ゼ","ze"},
                {"ゾ","zo"},{"ダ","da"},{"ヂ","ji"},{"ヅ","zu"},{"デ","de"},
                {"ド","do"},{"バ","ba"},{"ビ","bi"},{"ブ","bu"},{"ベ","be"},
                {"ボ","bo"},{"パ","pa"},{"ピ","pi"},{"プ","pu"},{"ペ","pe"},
                {"ポ","po"}
        };

        for (String[] pair : katakana) {
            JAPANESE_KATAKANA_MAP.put(pair[0].charAt(0), pair[1]);
        }

        // Arabic Transliteration
        String[][] arabic = {
                {"ا","a"},{"ب","b"},{"ت","t"},{"ث","th"},{"ج","j"},{"ح","h"},
                {"خ","kh"},{"د","d"},{"ذ","dh"},{"ر","r"},{"ز","z"},{"س","s"},
                {"ش","sh"},{"ص","s"},{"ض","d"},{"ط","t"},{"ظ","z"},{"ع","'"},
                {"غ","gh"},{"ف","f"},{"ق","q"},{"ك","k"},{"ل","l"},{"م","m"},
                {"ن","n"},{"ه","h"},{"و","w"},{"ي","y"},{"ء","'"},{"أ","a"},
                {"إ","i"},{"آ","aa"},{"ة","t"},{"ى","a"}
        };

        for (String[] pair : arabic) {
            if (pair[0].length() == 1) {
                ARABIC_MAP.put(pair[0].charAt(0), pair[1]);
            }
        }

        // Korean Hangul (Basic)
        String[][] korean = {
                {"ㄱ","g"},{"ㄴ","n"},{"ㄷ","d"},{"ㄹ","r"},{"ㅁ","m"},{"ㅂ","b"},
                {"ㅅ","s"},{"ㅇ",""},{"ㅈ","j"},{"ㅊ","ch"},{"ㅋ","k"},{"ㅌ","t"},
                {"ㅍ","p"},{"ㅎ","h"},{"ㅏ","a"},{"ㅑ","ya"},{"ㅓ","eo"},{"ㅕ","yeo"},
                {"ㅗ","o"},{"ㅛ","yo"},{"ㅜ","u"},{"ㅠ","yu"},{"ㅡ","eu"},{"ㅣ","i"},
                {"가","ga"},{"나","na"},{"다","da"},{"라","ra"},{"마","ma"},{"바","ba"},
                {"사","sa"},{"아","a"},{"자","ja"},{"차","cha"},{"카","ka"},{"타","ta"},
                {"파","pa"},{"하","ha"}
        };

        for (String[] pair : korean) {
            if (pair[0].length() == 1) {
                KOREAN_MAP.put(pair[0].charAt(0), pair[1]);
            }
        }

        // Russian Cyrillic
        String[][] russian = {
                {"а","a"},{"б","b"},{"в","v"},{"г","g"},{"д","d"},{"е","e"},
                {"ё","yo"},{"ж","zh"},{"з","z"},{"и","i"},{"й","y"},{"к","k"},
                {"л","l"},{"м","m"},{"н","n"},{"о","o"},{"п","p"},{"р","r"},
                {"с","s"},{"т","t"},{"у","u"},{"ф","f"},{"х","kh"},{"ц","ts"},
                {"ч","ch"},{"ш","sh"},{"щ","shch"},{"ъ",""},{"ы","y"},{"ь",""},
                {"э","e"},{"ю","yu"},{"я","ya"},{"А","A"},{"Б","B"},{"В","V"},
                {"Г","G"},{"Д","D"},{"Е","E"},{"Ё","Yo"},{"Ж","Zh"},{"З","Z"},
                {"И","I"},{"Й","Y"},{"К","K"},{"Л","L"},{"М","M"},{"Н","N"},
                {"О","O"},{"П","P"},{"Р","R"},{"С","S"},{"Т","T"},{"У","U"},
                {"Ф","F"},{"Х","Kh"},{"Ц","Ts"},{"Ч","Ch"},{"Ш","Sh"},{"Щ","Shch"},
                {"Ъ",""},{"Ы","Y"},{"Ь",""},{"Э","E"},{"Ю","Yu"},{"Я","Ya"}
        };

        for (String[] pair : russian) {
            if (pair[0].length() == 1) {
                RUSSIAN_MAP.put(pair[0].charAt(0), pair[1]);
            }
        }

        // Basic Chinese Pinyin mapping (simplified - common characters)
        String[][] chinese = {
                {"你","ni"},{"好","hao"},{"我","wo"},{"是","shi"},{"中","zhong"},
                {"国","guo"},{"人","ren"},{"们","men"},{"他","ta"},{"她","ta"},
                {"这","zhe"},{"那","na"},{"有","you"},{"在","zai"},{"不","bu"},
                {"了","le"},{"和","he"},{"对","dui"},{"吧","ba"},{"吗","ma"},
                {"啊","a"},{"哦","o"},{"嗯","en"},{"嗨","hai"},{"哈","ha"}
        };

        for (String[] pair : chinese) {
            if (pair[0].length() == 1) {
                CHINESE_PINYIN_MAP.put(pair[0].charAt(0), pair[1]);
            }
        }
    }

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
            String transliterated = null;

            // Hindi (Devanagari: U+0900 to U+097F)
            if (c >= '\u0900' && c <= '\u097F') {
                transliterated = HINDI_MAP.get(c);
            }
            // Japanese Hiragana (U+3040 to U+309F)
            else if (c >= '\u3040' && c <= '\u309F') {
                transliterated = JAPANESE_HIRAGANA_MAP.get(c);
            }
            // Japanese Katakana (U+30A0 to U+30FF)
            else if (c >= '\u30A0' && c <= '\u30FF') {
                transliterated = JAPANESE_KATAKANA_MAP.get(c);
            }
            // Arabic (U+0600 to U+06FF)
            else if (c >= '\u0600' && c <= '\u06FF') {
                transliterated = ARABIC_MAP.get(c);
            }
            // Korean Hangul (U+AC00 to U+D7AF)
            else if (c >= '\uAC00' && c <= '\uD7AF') {
                transliterated = KOREAN_MAP.get(c);
                if (transliterated == null) {
                    transliterated = String.valueOf(c);
                }
            }
            // Russian Cyrillic (U+0400 to U+04FF)
            else if (c >= '\u0400' && c <= '\u04FF') {
                transliterated = RUSSIAN_MAP.get(c);
            }
            // Chinese (Simplified/Traditional) (U+4E00 to U+9FFF)
            else if (c >= '\u4E00' && c <= '\u9FFF') {
                transliterated = CHINESE_PINYIN_MAP.get(c);
            }

            if (transliterated != null) {
                result.append(transliterated);
            } else {
                result.append(c);
            }
        }

        return result.toString();
    }
}