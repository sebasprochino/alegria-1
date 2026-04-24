export default function RadarStatus({ active }) {
  return (
    <div className="text-xs">
      Radar: {active ? "activo" : "en reposo"}
    </div>
  );
}
