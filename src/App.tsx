import type { FC } from 'react'
import Navbar from './components/Navbar'
import Hero from './components/Hero'
import Services from './components/Services'
import About from './components/About'
import Portfolio from './components/Portfolio'
import Technologies from './components/Technologies'
import Contact from './components/Contact'
import Footer from './components/Footer'

const App: FC = () => (
  <>
    <Navbar />
    <main>
      <Hero />
      <Services />
      <About />
      <Portfolio />
      <Technologies />
      <Contact />
    </main>
    <Footer />
  </>
)

export default App
