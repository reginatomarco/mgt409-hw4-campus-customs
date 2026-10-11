import { useEffect } from 'react'
import { Link, Route, Routes, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import ChatWidget from './components/ChatWidget'
import Home from './pages/Home'
import Products from './pages/Products'
import ProductPage from './pages/ProductPage'
import About from './pages/About'
import Login from './pages/Login'
import CreateAccount from './pages/CreateAccount'

export default function App() {
  const { pathname } = useLocation()
  // Start each new page at the top. Braces matter: scrollTo can return a Promise in some browsers.
  useEffect(() => {
    window.scrollTo(0, 0)
  }, [pathname])

  return (
    <>
      <NavBar />
      <main className="page">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/products/:productId" element={<ProductPage />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/create-account" element={<CreateAccount />} />
          <Route path="*" element={<Home />} />
        </Routes>
      </main>
      <footer className="footer">
        <div className="footer-inner">
          <div className="footer-brand">
            <span className="brand-mark">CC</span>
            <p>
              <strong>Campus Customs</strong>
              <br />
              Casual comfort. Unbreakable Bulldog pride.
            </p>
          </div>
          <div>
            <h4>Shop</h4>
            <Link to="/products?category=hoodies">Hoodies</Link>
            <Link to="/products?category=crewnecks">Crewnecks</Link>
            <Link to="/products?category=tees">Tees</Link>
            <Link to="/products?category=outerwear">Fleece & Jackets</Link>
          </div>
          <div>
            <h4>Store</h4>
            <Link to="/about">About Us</Link>
            <Link to="/login">Log in</Link>
            <Link to="/create-account">Create Account</Link>
          </div>
          <div>
            <h4>Visit</h4>
            <p>
              57 Broadway
              <br />
              New Haven, CT 06511
            </p>
          </div>
        </div>
        <p className="footer-fine">© Campus Customs · Officially licensed Yale apparel · Boola Boola</p>
      </footer>
      <ChatWidget />
    </>
  )
}
