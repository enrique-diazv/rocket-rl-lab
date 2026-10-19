import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

type EvaluationSuccessChartProps = {
  successRate: number
}

export function EvaluationSuccessChart({
  successRate,
}: EvaluationSuccessChartProps) {
  const data = [
    { outcome: 'Exitosos', percentage: successRate },
    { outcome: 'No exitosos', percentage: 100 - successRate },
  ]

  return (
    <figure style={{ margin: 0 }}>
      <h3>Resultado de los aterrizajes (%)</h3>

      <ResponsiveContainer width="100%" height={300} minWidth={0}>
        <BarChart
          data={data}
          margin={{ top: 10, right: 20, bottom: 10, left: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="outcome" />
          <YAxis
            domain={[0, 100]}
            tickFormatter={value => `${value} %`}
          />
          <Tooltip
            formatter={value =>
              typeof value === 'number'
                ? `${value.toFixed(1)} %`
                : value
            }
          />
          <Bar
            dataKey="percentage"
            name="Porcentaje de episodios"
            fill="#f59e0b"
            isAnimationActive={false}
          />
        </BarChart>
      </ResponsiveContainer>
    </figure>
  )
}