import { useState } from 'react'
import type { FC, FormEvent } from 'react'
import { COMPANY } from '../data/content'
import Reveal from './Reveal'
import SectionTitle from './SectionTitle'

interface FormData {
  name: string
  email: string
  message: string
}

type FormErrors = Partial<Record<keyof FormData, string>>

const EMPTY_FORM: FormData = { name: '', email: '', message: '' }
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate(form: FormData): FormErrors {
  const errors: FormErrors = {}
  if (form.name.trim().length < 2) errors.name = '⚠ Ingresa tu nombre (mínimo 2 caracteres)'
  if (!EMAIL_REGEX.test(form.email)) errors.email = '⚠ Ingresa un correo válido'
  if (form.message.trim().length < 10) errors.message = '⚠ Cuéntanos un poco más (mínimo 10 caracteres)'
  return errors
}

const INPUT_CLASS =
  'w-full border-2 bg-[#0a0a0a] px-4 py-3 text-sm text-white placeholder-zgray/50 outline-none transition-colors focus:border-primary'

const Contact: FC = () => {
  const [form, setForm] = useState<FormData>(EMPTY_FORM)
  const [errors, setErrors] = useState<FormErrors>({})
  const [sent, setSent] = useState(false)

  const handleChange = (field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }))
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }))
  }

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const nextErrors = validate(form)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    // Sin backend: abre el cliente de correo con el mensaje prellenado
    const subject = encodeURIComponent(`Contacto desde el sitio web — ${form.name}`)
    const body = encodeURIComponent(`${form.message}\n\n— ${form.name} (${form.email})`)
    window.location.href = `mailto:${COMPANY.email}?subject=${subject}&body=${body}`

    setSent(true)
    setForm(EMPTY_FORM)
  }

  const borderFor = (field: keyof FormData) => (errors[field] ? 'border-red-500' : 'border-zgray/40')

  return (
    <section id="contacto" className="relative bg-black py-24">
      <div className="mx-auto max-w-6xl px-4 sm:px-6">
        <SectionTitle
          eyebrow="HABLEMOS"
          title="CONTACTO"
          subtitle="¿Tienes un proyecto en mente? Presiona START y conversemos."
        />

        <div className="grid grid-cols-1 gap-10 lg:grid-cols-5">
          {/* Datos de la empresa */}
          <Reveal className="lg:col-span-2">
            <div className="pixel-corners h-full border-2 border-accent/50 bg-[#0a0a0a] p-8">
              <h3 className="font-brand text-sm text-primary">ZENTROX</h3>
              <p className="mt-3 text-sm text-zgray">{COMPANY.slogan}</p>

              <ul className="mt-8 space-y-5 text-sm">
                <li className="flex items-start gap-3">
                  <span className="font-brand text-accent" aria-hidden="true">▸</span>
                  <div>
                    <p className="font-brand text-[9px] text-zgray">UBICACIÓN</p>
                    <p className="mt-1 text-cream">{COMPANY.location}</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="font-brand text-accent" aria-hidden="true">▸</span>
                  <div>
                    <p className="font-brand text-[9px] text-zgray">CORREO</p>
                    <a href={`mailto:${COMPANY.email}`} className="mt-1 block text-cream hover:text-primary transition-colors break-all">
                      {COMPANY.email}
                    </a>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="font-brand text-accent" aria-hidden="true">▸</span>
                  <div>
                    <p className="font-brand text-[9px] text-zgray">TELÉFONO</p>
                    <a href={`tel:${COMPANY.phone.replace(/[^+\d]/g, '')}`} className="mt-1 block text-cream hover:text-primary transition-colors">
                      {COMPANY.phone}
                    </a>
                  </div>
                </li>
              </ul>

              <div className="mt-10 border-t-2 border-dashed border-zgray/30 pt-6">
                <p className="font-brand text-[9px] leading-relaxed text-zgray">
                  INSERT COIN TO CONTINUE…
                  <span className="text-primary"> ●</span>
                </p>
              </div>
            </div>
          </Reveal>

          {/* Formulario */}
          <Reveal delay={120} className="lg:col-span-3">
            <form onSubmit={handleSubmit} noValidate className="pixel-corners border-2 border-zgray/30 bg-[#0a0a0a] p-8">
              {sent && (
                <div className="mb-6 border-2 border-primary bg-primary/10 p-4" role="status">
                  <p className="font-brand text-[10px] leading-relaxed text-primary">
                    ★ ¡MENSAJE LISTO! SE ABRIÓ TU CLIENTE DE CORREO PARA ENVIARLO. ★
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 gap-5 sm:grid-cols-2">
                <div>
                  <label htmlFor="name" className="mb-2 block font-brand text-[9px] text-cream">
                    NOMBRE *
                  </label>
                  <input
                    id="name"
                    type="text"
                    value={form.name}
                    onChange={(e) => handleChange('name', e.target.value)}
                    placeholder="Tu nombre"
                    className={`${INPUT_CLASS} ${borderFor('name')}`}
                  />
                  {errors.name && <p className="mt-2 text-xs text-red-400">{errors.name}</p>}
                </div>

                <div>
                  <label htmlFor="email" className="mb-2 block font-brand text-[9px] text-cream">
                    CORREO *
                  </label>
                  <input
                    id="email"
                    type="email"
                    value={form.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    placeholder="tucorreo@ejemplo.com"
                    className={`${INPUT_CLASS} ${borderFor('email')}`}
                  />
                  {errors.email && <p className="mt-2 text-xs text-red-400">{errors.email}</p>}
                </div>
              </div>

              <div className="mt-5">
                <label htmlFor="message" className="mb-2 block font-brand text-[9px] text-cream">
                  MENSAJE *
                </label>
                <textarea
                  id="message"
                  rows={6}
                  value={form.message}
                  onChange={(e) => handleChange('message', e.target.value)}
                  placeholder="Cuéntanos sobre tu proyecto…"
                  className={`${INPUT_CLASS} resize-none ${borderFor('message')}`}
                />
                {errors.message && <p className="mt-2 text-xs text-red-400">{errors.message}</p>}
              </div>

              <button
                type="submit"
                className="pixel-corners glitch-hover mt-8 w-full bg-primary px-8 py-4 font-brand text-xs text-black transition-colors hover:bg-accent sm:w-auto"
              >
                ▶ ENVIAR MENSAJE
              </button>
            </form>
          </Reveal>
        </div>
      </div>
    </section>
  )
}

export default Contact
