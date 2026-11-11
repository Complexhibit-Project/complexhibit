import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Privacy Policy | Complexhibit",
  description: "Privacy Policy for Complexhibit, an ontology-based exhibition explorer developed by iArtHIS_lab.",
};

export default function PrivacyPolicy() {
  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return (
    <div className="bg-white py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">Privacy Policy</h1>
          <p className="mt-2 text-lg leading-8 text-gray-600">
            Last updated: {currentDate}
          </p>
        </div>

        <div className="mt-16 text-lg leading-8 text-gray-600 space-y-8">
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">1. Introduction</h2>
            <p>
              Welcome to <strong>Complexhibit</strong> (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;). We are committed to protecting your privacy and ensuring your personal data is handled in compliance with applicable laws, including the General Data Protection Regulation (GDPR). 
              This Privacy Policy explains how we collect, use, and safeguard your information when you visit our website.
            </p>
            <p className="mt-4">
              Complexhibit is a research project developed by <strong>iArtHIS_lab</strong> at the <strong>Universidad de Málaga</strong>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">2. Information We Collect</h2>
            <p>
              As a research-focused platform, we collect minimal personal data. The types of information we may collect include:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>
                <strong>Log Data:</strong> Like most websites, our servers automatically record information that your browser sends whenever you visit the site. This may include your IP address, browser type, the pages of our site that you visit, the time spent on those pages, and other statistics.
              </li>
              <li>
                <strong>Cookies:</strong> We use cookies solely for the functional operation of the website and to improve your user experience. We do not use cookies for advertising or tracking purposes across other sites.
              </li>
              <li>
                <strong>Communications:</strong> If you contact us via email, we may retain your contact information and the content of your message to respond to your inquiry.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p>
              We use the collected information for the following purposes:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li>To provide and maintain the Complexhibit platform.</li>
              <li>To monitor the usage of our service for research and optimization purposes.</li>
              <li>To detect, prevent, and address technical issues.</li>
              <li>To communicate with you regarding your inquiries or feedback.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">4. Data Sharing and Disclosure</h2>
            <p>
              We do not sell, trade, or otherwise transfer your personal information to outside parties. We may share generic aggregated demographic information not linked to any personal identification information with our research partners and trusted affiliates for the purposes outlined above.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">5. Your Data Rights</h2>
            <p>
              Under the GDPR, you have the following rights regarding your personal data:
            </p>
            <ul className="list-disc pl-6 mt-4 space-y-2">
              <li><strong>Right to Access:</strong> You have the right to request copies of your personal data.</li>
              <li><strong>Right to Rectification:</strong> You have the right to request that we correct any information you believe is inaccurate.</li>
              <li><strong>Right to Erasure:</strong> You have the right to request that we erase your personal data, under certain conditions.</li>
            </ul>
            <p className="mt-4">
              To exercise these rights, please contact us at the email provided below.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">6. External Links</h2>
            <p>
              Our website may contain links to external sites that are not operated by us (e.g., social media profiles, partner institutions). We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">7. Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy, please contact us:
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <p className="font-semibold text-gray-900">iArtHIS_lab - Universidad de Málaga</p>
              <p className="mt-1">
                Email: <a href="mailto:contact@complexhibit.org" className="text-indigo-600 hover:text-indigo-500">contact@complexhibit.org</a>
              </p>
              <p className="mt-1">
                Website: <a href="https://iarthis.iarthislab.eu/" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-500">https://iarthis.iarthislab.eu/</a>
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
