export default function TestimonialSection() {
  return (
    <section>
      <div className="py-24">
        <div className="mx-auto w-full max-w-5xl px-6">
          <blockquote className="before:bg-mastercard-orange relative max-w-xl pl-6 before:absolute before:inset-y-0 before:left-0 before:w-1 before:rounded-full">
            <p className="text-gray-900 text-lg">
              Mastercard объединяет и расширяет возможности цифровой экономики, делая транзакции безопасными, простыми и доступными для всех. Наши инновации помогают людям и бизнесу реализовать их величайший потенциал.
            </p>
            <footer className="mt-4 flex items-center gap-2">
              <cite className="font-medium">Mastercard</cite>
              <span
                aria-hidden
                className="bg-gray-300 size-1 rounded-full"
              ></span>
              <span className="text-gray-600">Глобальная платежная сеть</span>
            </footer>
          </blockquote>
        </div>
      </div>
    </section>
  );
}
