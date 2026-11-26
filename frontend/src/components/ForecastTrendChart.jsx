import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

function ForecastTrendChart({ data }) {
  return (
    <ResponsiveContainer height="100%" minHeight={240} width="100%">
      <LineChart data={data} margin={{ top: 10, right: 12, bottom: 0, left: -18 }}>
        <CartesianGrid stroke="#edf0f4" strokeDasharray="3 5" vertical={false} />
        <XAxis
          axisLine={false}
          dataKey="label"
          interval="preserveStartEnd"
          tick={{ fill: '#8a95a5', fontSize: 11 }}
          tickLine={false}
          tickMargin={10}
        />
        <YAxis
          axisLine={false}
          tick={{ fill: '#8a95a5', fontSize: 11 }}
          tickFormatter={(value) => `${value}°`}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{
            border: '1px solid #e7ebf2',
            borderRadius: 10,
            boxShadow: '0 8px 24px rgb(26 44 66 / 10%)',
          }}
          formatter={(value, name) => {
            if (name === 'temperature') {
              return [`${Number(value).toFixed(1)} °C`, 'Air temperature']
            }
            if (name === 'apparent_temperature_c') {
              return [`${Number(value).toFixed(1)} °C`, 'Feels like']
            }
            return [
              item.payload.heat_risk?.risk_level ?? 'Not applicable',
              'Heat risk',
            ]
          }}
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

export default ForecastTrendChart
