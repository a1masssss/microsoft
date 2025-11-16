import { PromptBox } from './chatgpt-prompt-input';

export function PromptBoxDemo() {
  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const message = formData.get('message');

    if (!message && !event.currentTarget.querySelector('img')) {
      return;
    }

    alert('Message Submitted!');
  };

  return (
    <div className="flex min-h-screen w-full flex-col items-center justify-center bg-background p-4 dark:bg-[#212121]">
      <div className="flex w-full max-w-xl flex-col gap-10">
        <p className="text-center text-3xl text-foreground">How Can I Help You</p>
        <form onSubmit={handleSubmit}>
          <PromptBox name="message" />
        </form>
      </div>
    </div>
  );
}
