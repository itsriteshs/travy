import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    extend: {
      colors: {
        travyCream: "#FFF7E8",
        travyPaper: "#FFFFFF",
        travyInk: "#111111",
        travySunwash: "#FFEFB8",
        travyYellow: "#FFD84D",
        travyYellowHover: "#FFC928",
        travyBlue: "#4DA3FF",
        travyPink: "#FF70B8",
        travyMint: "#7CF7B3",
        travyGreen: "#3EE37A",
        travyOrange: "#FF9F43",
        travyLavender: "#B9A7FF",
        travyDanger: "#FF4D4D",
        travyWarning: "#FFB020",
        travyInfo: "#38BDF8"
      },
      boxShadow: {
        neoSm: "2px 2px 0px #000",
        neo: "4px 4px 0px #000",
        neoLg: "6px 6px 0px #000",
        neoXl: "10px 10px 0px #000"
      },
      borderRadius: {
        neo: "6px",
        neoLg: "8px"
      }
    }
  },
  plugins: []
};

export default config;
