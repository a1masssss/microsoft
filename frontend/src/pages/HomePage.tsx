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
      <section className="bg-gradient-to-r from-mastercard-red via-mastercard-orange to-mastercard-yellow text-white">
        <div className="max-w-7xl mx-auto px-4 py-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <div className="flex items-center justify-center mb-6">
              <div className="w-16 h-16 rounded-full bg-mastercard-red" />
              <div className="w-16 h-16 rounded-full bg-mastercard-orange -ml-8" />
            </div>
            <h1 className="text-4xl font-bold mb-4">Mastercard</h1>

            {/* Animated Shiny Text */}
            <div className="mb-6">
              <div
                className="group rounded-full border border-white/20 bg-white/10 text-base text-white transition-all ease-in hover:cursor-pointer hover:bg-white/20 inline-block"
              >
                <AnimatedShinyText className="inline-flex items-center justify-center px-4 py-1 transition ease-out hover:text-white/80 hover:duration-300 text-white">
                  <span>✨ Цифровые платежи будущего</span>
                  <ArrowRight className="ml-1 size-3 transition-transform duration-300 ease-in-out group-hover:translate-x-0.5" />
                </AnimatedShinyText>
              </div>
            </div>

            <p className="text-xl text-white/90 max-w-2xl mx-auto">
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
                <div className="w-12 h-12 rounded-full bg-gradient-to-r from-mastercard-orange to-mastercard-red flex items-center justify-center mb-4">
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

      {/* About Section */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <div className="bg-white rounded-2xl p-8 shadow-sm border border-gray-100">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">О Mastercard</h2>
          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 mb-4">
              Mastercard — глобальная технологическая компания в платежной индустрии. Наша миссия — объединить и расширить
              возможности цифровой экономики, которая приносит пользу всем и везде, делая транзакции безопасными, простыми,
              умными и доступными.
            </p>
            <p className="text-gray-600">
              Используя безопасные данные и сети, партнерства и страсть, наши инновации и решения помогают людям, финансовым
              учреждениям, правительствам и бизнесу реализовать их величайший потенциал.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
