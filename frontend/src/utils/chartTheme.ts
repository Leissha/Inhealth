export function getThemeColor(token: string): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue(token).trim()
  return `hsl(${value})`
}

export function getChartTheme() {
  return {
    primary: getThemeColor('--chart-primary'),
    primarySoft: getThemeColor('--surface-blue'),
    foreground: getThemeColor('--foreground'),
    mutedForeground: getThemeColor('--muted-foreground'),
    grid: getThemeColor('--chart-grid'),
  }
}
