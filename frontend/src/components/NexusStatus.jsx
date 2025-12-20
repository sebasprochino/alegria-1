export default function NexusStatus({ active }) {
  return (
    <div className="text-xs">
      Nexus: {active ? "memoria presente" : "memoria desconectada"}
    </div>
  );
}
