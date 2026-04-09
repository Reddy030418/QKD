import 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    name: 'light' | 'dark';
    colors: {
      background: string;
      backgroundGradientStart: string;
      backgroundGradientEnd: string;
      text: string;
      mutedText: string;
      cardBackground: string;
      cardBorder: string;
      accent: string;
      accentHover: string;
      danger: string;
    };
  }
}

