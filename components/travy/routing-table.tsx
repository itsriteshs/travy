import { NeoCard, NeoCardTitle } from "@/components/ui/neo-card";

type RoutingRow = {
  step?: number;
  task: string;
  route: string;
  cost: string;
  reason: string;
};

export function RoutingTable({
  rows,
  title = "Routing Decision Table"
}: {
  rows: RoutingRow[];
  title?: string;
}) {
  return (
    <NeoCard tone="paper" strong>
      <NeoCardTitle className="mb-4">{title}</NeoCardTitle>
      <div className="overflow-x-auto neo-scrollbar">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className="border-b-2 border-black bg-travyBlue">
              {rows.some((row) => row.step) && <th className="p-2 font-black">Step</th>}
              <th className="p-2 font-black">Task</th>
              <th className="p-2 font-black">Route</th>
              <th className="p-2 font-black">Cost</th>
              <th className="p-2 font-black">Reason</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.step || row.task}-${row.task}`} className="border-b-2 border-black bg-white">
                {rows.some((item) => item.step) && (
                  <td className="p-2 font-mono font-black">{row.step}</td>
                )}
                <td className="p-2 font-bold">{row.task}</td>
                <td className="p-2 font-black">{row.route}</td>
                <td className="p-2 font-mono font-black">{row.cost}</td>
                <td className="p-2 font-semibold">{row.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </NeoCard>
  );
}
