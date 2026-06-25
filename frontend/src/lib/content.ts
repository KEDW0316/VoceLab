import type { Lang } from "./i18n";

// 스케일 영어 이름/설명/음절 (백엔드는 한국어 데이터를 줌 → EN은 여기서 덮어씀)
export const SCALE_EN: Record<string, { name: string; desc: string; syllable: string }> = {
  five_tone: { name: "5-tone scale", desc: "Do-Re-Mi-Fa-Sol-Fa-Mi-Re-Do. The most basic pitch warm-up; move up by semitones.", syllable: "ma" },
  major_octave: { name: "Major scale (octave)", desc: "A full octave up and down for even, connected tone.", syllable: "ah" },
  major_triad: { name: "Arpeggio (triad)", desc: "Do-Mi-Sol-Do-Sol-Mi-Do. Harmonic pitch sense and range.", syllable: "mo" },
  arpeggio_top_hold: { name: "Arpeggio (hold top note)", desc: "Holds the octave top note ×3 for high-note support and consistency.", syllable: "mo" },
  octave_arp_10th: { name: "Extended arpeggio (10th)", desc: "Reaches up to the 10th above the octave. Opens the upper range.", syllable: "ah" },
  dominant7_arp: { name: "Dominant 7th arpeggio", desc: "Do-Mi-Sol-B♭-Do. Maj3/P5/min7/octave leaps for harmony and pitch.", syllable: "mo" },
  minor_triad: { name: "Minor triad arpeggio", desc: "Do-E♭-Sol-Do. Minor-key pitch sense and chord accuracy.", syllable: "no" },
  major_ninth: { name: "Long scale (9th)", desc: "1.5 octaves up to the 9th and back. Range extension and endurance.", syllable: "ah" },
  descending_5tone: { name: "Descending 5-tone", desc: "Sol-Fa-Mi-Re-Do. Coming down for larynx stability and legato.", syllable: "ne" },
  trill: { name: "Trill (whole tone)", desc: "Quickly alternate two notes. Agility and vocal-fold flexibility.", syllable: "ah" },
  staccato_arp: { name: "Staccato arpeggio", desc: "Do-Mi-Sol-Mi-Do, short and detached. Agility and clean onset.", syllable: "he" },
  octave_jump: { name: "Octave jump", desc: "Do—high Do—Do. Wide interval leaps.", syllable: "oo" },
  perfect_fifth: { name: "Perfect 5th (Do-Sol-Do)", desc: "Steady pitch and a sense of support.", syllable: "ah" },
  chromatic5: { name: "Chromatic (semitones)", desc: "Five notes by semitone, up and down. Fine pitch control.", syllable: "ne" },
  lip_trill: { name: "Lip trill (5-tone)", desc: "5-tone on a lip trill (brr). SOVT semi-occluded warm-up.", syllable: "lip trill (brr)" },
  sustained_vowel: { name: "Sustained vowel (long tone)", desc: "Hold one note. Best for CPPS/jitter/shimmer/HNR; breath support.", syllable: "ah" },
  siren: { name: "Siren (glide)", desc: "Glide an octave up and down without breaks. Smoothly connects the range.", syllable: "ng" },
};

// 핵심 지표 영어 라벨/설명/정상범위
export const METRIC_EN: Record<string, { label: string; desc: string; normal: string }> = {
  cpps: { label: "CPPS", desc: "Cepstral Peak Prominence — higher = clearer, more stable voice.", normal: "≥ 4 dB" },
  hnr: { label: "HNR", desc: "Harmonics-to-noise ratio — higher = cleaner (less breathy).", normal: "≥ 20 dB" },
  jitter: { label: "Jitter", desc: "Cycle-to-cycle frequency perturbation — lower = steadier pitch.", normal: "< 1%" },
  shimmer: { label: "Shimmer", desc: "Cycle-to-cycle amplitude perturbation — lower = steadier loudness.", normal: "< 3.8%" },
};

const KO_NOTE: Record<string, string> = {
  C: "도", "C#": "도#", D: "레", "D#": "레#", E: "미", F: "파",
  "F#": "파#", G: "솔", "G#": "솔#", A: "라", "A#": "라#", B: "시",
};
const SOLFEGE_EN: Record<string, string> = {
  도: "Do", 레: "Re", 미: "Mi", 파: "Fa", 솔: "Sol", 라: "La", 시: "Ti",
};

// 실시간 음정 표시: ko=한국 보컬 옥타브(과학적-2)+도레미, en=과학적 음이름
export function pitchDisplay(note: string, octave: number, lang: Lang): { oct: string; name: string } {
  if (lang === "ko") return { oct: `${octave - 2}옥`, name: KO_NOTE[note] ?? note };
  return { oct: String(octave), name: note };
}

// 솔페지 토큰 변환 (도 레 미 → Do Re Mi). ˙(옥타브 위)는 ' 로.
export function solfegeTokens(solfege: string, lang: Lang): string[] {
  const toks = solfege.split(" ").filter(Boolean);
  if (lang === "ko") return toks;
  return toks.map((tok) => {
    const dots = (tok.match(/˙/g) || []).length;
    const base = tok.replace(/[˙#♭]/g, "");
    const acc = (tok.match(/[#♭]/g) || []).join("");
    return (SOLFEGE_EN[base] ?? base) + acc + "'".repeat(dots);
  });
}
