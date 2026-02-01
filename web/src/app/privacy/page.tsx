import Link from "next/link";

export const metadata = {
  title: "Privacy Policy - Jobflow",
};

export default function PrivacyPolicyPage() {
  return (
    <main className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Privacy Policy</h1>

      <div className="prose prose-gray max-w-none space-y-6">
        <p className="text-gray-600">
          Last updated: February 2026
        </p>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">1. Information We Collect</h2>
          <p>When you use Jobflow, we collect:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account information:</strong> Your name and email address from your OAuth provider (Google or GitHub)</li>
            <li><strong>Job data:</strong> URLs you submit and the job posting information extracted from them (title, company, location, salary, description)</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">2. How We Use Your Information</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li>To provide and maintain the job tracking service</li>
            <li>To associate your saved jobs with your account</li>
            <li>To authenticate your identity when you sign in</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">3. Data Storage</h2>
          <p>
            Your data is stored securely in our database. We do not sell, trade, or transfer your personal information to third parties.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">4. Your Rights (GDPR)</h2>
          <p>Under GDPR, you have the right to:</p>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Access:</strong> Export your jobs as CSV from the main dashboard</li>
            <li><strong>Rectification:</strong> Edit your job details at any time</li>
            <li><strong>Erasure:</strong> Delete your account and all associated data using the "Delete Account" button</li>
            <li><strong>Portability:</strong> Download your data in CSV format</li>
          </ul>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">5. Cookies</h2>
          <p>
            We use essential cookies only for authentication (session management). We do not use tracking or advertising cookies.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">6. Data Retention</h2>
          <p>
            Your data is retained until you delete your account. Upon account deletion, all your personal data and saved jobs are permanently removed from our systems.
          </p>
        </section>

        <section>
          <h2 className="text-xl font-semibold mt-8 mb-4">7. Contact</h2>
          <p>
            For any privacy-related questions, please contact us through our GitHub repository.
          </p>
        </section>

        <div className="mt-12 pt-8 border-t">
          <Link href="/" className="text-blue-600 hover:underline">
            &larr; Back to Home
          </Link>
        </div>
      </div>
    </main>
  );
}
