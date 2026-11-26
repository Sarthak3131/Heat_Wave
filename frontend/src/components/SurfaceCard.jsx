function SurfaceCard({ className = '', children, ...props }) {
  return (
    <section className={`surface-card ${className}`.trim()} {...props}>
      {children}
    </section>
  )
}

export default SurfaceCard
