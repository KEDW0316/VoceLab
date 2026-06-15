// 가벼운 localStorage 래퍼 (장치 선택·설정 기억용).

const PREFIX = "vocelab.";

export function loadPref(key: string): string | null {
  try {
    return localStorage.getItem(PREFIX + key);
  } catch {
    return null;
  }
}

export function savePref(key: string, value: string): void {
  try {
    localStorage.setItem(PREFIX + key, value);
  } catch {
    /* 무시 */
  }
}
