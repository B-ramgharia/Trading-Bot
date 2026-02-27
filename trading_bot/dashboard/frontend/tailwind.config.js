/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#0a0b0d",
                card: "#16181c",
                primary: "#f3ba2f", // Binance Yellow
                secondary: "#2b2f36",
                success: "#0ecb81",
                danger: "#f6465d",
            },
            backdropBlur: {
                xs: '2px',
            }
        },
    },
    plugins: [],
}
