import { useEffect } from "react";

declare global {
    interface Window {
        ChatWidget: any;
    }
}

export const ChatWidgetComponent: React.FC = () => {
    useEffect(() => {
        const script = document.createElement("script");
        script.src =
            "https://cdn.jsdelivr.net/npm/iaigroup-chatwidget@latest/build/bundle.min.js";
        script.async = true;
        script.onload = () => {
            // @ts-ignore
            ChatWidget({
                name: "Chatbot",
                serverUrl: "",
                useFeedback: true,
                useLogin: true,
            });

            // Apply custom black text to widget
            const style = document.createElement("style");
            style.innerHTML = `
        #chatWidgetContainer * {
          color: black !important; /* Force all text to black */
        }
      `;
            document.head.appendChild(style);
        };
        document.body.appendChild(script);
    }, []);

    return <div id="chatWidgetContainer"></div>;
};