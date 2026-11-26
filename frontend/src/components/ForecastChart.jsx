import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function ForecastChart({ data }) {
  return (
    <ResponsiveContainer height="100%" minHeight={190} width="100%">
      <LineChart
        data={data}
        margin={{ top: 8, right: 12, bottom: 0, left: -18 }}
      >
        <CartesianGrid
          stroke="#edf0f4"
          strokeDasharray="3 5"
          vertical={false}
        />
        <XAxis
          axisLine={false}
          dataKey="label"
          tick={{ fill: '#8a95a5', fontSize: 11 }}
          tickLine={false}
          tickMargin={10}
          interval="preserveStartEnd"
        />
        <YAxis
          axisLine={false}
          tick={{ fill: '#8a95a5', fontSize: 11 }}
          tickLine={false}
          tickFormatter={(value) => `${value}°`}
        />
        <Tooltip
          contentStyle={{
            border: '1px solid #e7ebf2',
            borderRadius: 10,
            boxShadow: '0 8px 24px rgb(26 44 66 / 10%)',
          }}
          formatter={(value, name) => [
            value == null ? 'Not available' : `${Number(value).toFixed(1)} °C`,
            name === 'temperature' ? 'Air temperature' : 'Feels like',
          ]}
          labelStyle={{ color: '#526176', fontWeight: 700 }}
        />
        <Line
          activeDot={{ r: 4, strokeWidth: 0 }}
          connectNulls={false}
          dataKey="temperature"
          dot={false}
          name="temperature"
          stroke="#e9a23b"
          strokeWidth={2.5}
          type="monotone"
        />
        <Line
          activeDot={{ r: 4, strokeWidth: 0 }}
          connectNulls={false}
          dataKey="apparent_temperature_c"
          dot={false}
          name="apparent_temperature_c"
          stroke="#7199c2"
          strokeDasharray="5 4"
          strokeWidth={2}
          type="monotone"
        />
      </LineChart>
    </ResponsiveContainer>
  )
}

export default ForecastChart
