export default function AnimaPresence({ state }) {
  return (
    <div className="text-xl text-center max-w-xl">
      {state === "thinking" && "Anima está pensando…"}
      {state === "listening" && "Anima está escuchando."}
      {state === "responding" && "Anima responde con cuidado."}
    </div>
  );
}
