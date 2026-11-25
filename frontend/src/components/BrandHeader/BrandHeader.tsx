import './BrandHeader.css'

export function BrandHeader() {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label="Sign al home">
        <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
        <span className="brand-name">sign<span>al</span></span>
      </a>
      <div className="header-tools">
        <span className="prototype-status"><i /> LOCAL PROTOTYPE</span>
        <a className="header-about" href="#about">About <span aria-hidden="true">↗</span></a>
      </div>
    </header>
  )
}
