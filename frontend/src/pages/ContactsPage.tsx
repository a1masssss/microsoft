import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Globe } from 'lucide-react';

export const ContactsPage = () => {
  const contacts = [
    {
      icon: Phone,
      title: 'Телефон',
      value: '+7 (727) 123-45-67',
      description: 'Горячая линия 24/7',
    },
    {
      icon: Mail,
      title: 'Email',
      value: 'support@mastercard.kz',
      description: 'Ответим в течение 24 часов',
    },
    {
      icon: MapPin,
      title: 'Адрес',
      value: 'г. Алматы, ул. Достык 123',
      description: 'Главный офис в Казахстане',
    },
    {
      icon: Globe,
      title: 'Веб-сайт',
      value: 'www.mastercard.kz',
      description: 'Официальный сайт',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <section className="border-b border-gray-200 bg-white">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center"
          >
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Контакты</h1>
            <p className="text-gray-500">Мы всегда готовы помочь вам</p>
          </motion.div>
        </div>
      </section>

      {/* Contacts Grid */}
      <section className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-2 gap-4">
          {contacts.map((contact, index) => {
            const Icon = contact.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
              >
                <div className="flex items-start gap-4">
                  <div className="w-12 h-12 rounded-full bg-gray-900 flex items-center justify-center flex-shrink-0">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-1">{contact.title}</h3>
                    <p className="text-gray-900 font-medium mb-1">{contact.value}</p>
                    <p className="text-sm text-gray-600">{contact.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Support Info */}
      <section className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Служба поддержки</h2>
          <p className="text-gray-600 mb-4">
            Наша команда всегда готова ответить на ваши вопросы и помочь решить любые проблемы.
            Вы можете связаться с нами любым удобным способом.
          </p>
          <div className="flex gap-3">
            <button className="px-6 py-2 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors">
              Написать нам
            </button>
            <button className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors">
              Позвонить
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
