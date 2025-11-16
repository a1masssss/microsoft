import { motion } from 'framer-motion';
import { CreditCard, Globe, Shield, Zap, ArrowRight } from 'lucide-react';
import { AnimatedShinyText } from '../components/ui/animated-shiny-text';
import TestimonialSection from '../components/ui/testimonials';

export const HomePage = () => {
  const features = [
    {
      icon: CreditCard,
      title: 'Безопасные платежи',
      description: 'Надежная защита ваших транзакций по всему миру',
    },
    {
      icon: Globe,
      title: 'Глобальное покрытие',
      description: 'Принимается в более чем 210 странах и территориях',
    },
    {
      icon: Shield,
      title: 'Защита данных',
      description: 'Современные технологии безопасности и шифрования',
    },
    {
      icon: Zap,
      title: 'Мгновенные переводы',
      description: 'Быстрые и удобные денежные переводы',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="border-b border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center mb-4">
              <div className="h-1.5 w-24 rounded-full bg-gradient-to-r from-[#ff9966] to-[#ff5e62]" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Mastercard</h1>

            {/* Animated Shiny Text */}
            <div className="mb-6">
              <div className="group inline-flex rounded-full border border-gray-200 bg-gray-50 text-base text-gray-900 transition-all hover:bg-white">
                <AnimatedShinyText className="inline-flex items-center justify-center px-4 py-1 text-gray-900 transition ease-out group-hover:text-gray-600">
                  <span>✨ Цифровые платежи будущего</span>
                  <ArrowRight className="ml-1 size-3 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5" />
                </AnimatedShinyText>
              </div>
            </div>

            <p className="mx-auto max-w-2xl text-xl text-gray-600">
              Бесценные возможности для вашего бизнеса и личных финансов
            </p>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow border border-gray-100"
              >
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-[#ff9966] to-[#ff5e62] flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Testimonial Section */}
      <TestimonialSection />

    
    </div>
  );
};
