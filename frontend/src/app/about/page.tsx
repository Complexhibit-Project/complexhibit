import Link from 'next/link';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "About Us | Complexhibit",
  description: "Learn about Complexhibit, an ontology-based exhibition explorer developed by iArtHIS_lab.",
};

export default function AboutPage() {
  return (
    <div className="bg-white py-16 sm:py-24">
      <div className="mx-auto max-w-3xl px-6 lg:px-8">
        <div className="mx-auto max-w-2xl text-center">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">About Complexhibit</h1>
          <p className="mt-6 text-lg leading-8 text-gray-600">
            Exploring the interconnected world of art exhibitions through Semantic Web technologies.
          </p>
        </div>

        <div className="mt-16 text-lg leading-8 text-gray-600 space-y-8">
          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">Our Vision</h2>
            <p>
              <strong>Complexhibit</strong> is a cutting-edge platform designed to explore the interconnected world of art exhibitions, actors, and artworks through the power of Semantic Web technologies.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">Our Mission</h2>
            <p>
              Our mission is to provide researchers, art historians, and the general public with a structured and rich interface to navigate complex cultural data. By leveraging ontologies and mapped data, we uncover hidden relationships and provide deep insights into the history of exhibitions.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">The Technology</h2>
            <p>
              Complexhibit is built upon a robust knowledge graph, utilizing standards like <strong>RDF</strong>, <strong>SPARQL</strong>, and <strong>OWL</strong>. This allows for precise querying and data interconnection that traditional databases cannot match. The backend is powered by modern semantic engines, while the frontend delivers a seamless exploration experience.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold tracking-tight text-gray-900 mb-4">Get in Touch</h2>
            <p>
              We value community feedback to improve our data quality and platform features.
            </p>
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
               <p className="font-semibold text-gray-900">Complexhibit Team</p>
               <p className="mt-1">
                 Email: <a href="mailto:nro@uma.es" className="text-indigo-600 hover:text-indigo-500">nro@uma.es</a>
               </p>
               <p className="mt-1">
                 Report Incidents: <Link href="/reports" className="text-indigo-600 hover:text-indigo-500 underline">Visit Report Page</Link>
               </p>
               <p className="mt-1 flex items-center gap-1">
                 Developed by <a href="https://iarthis.iarthislab.eu/" target="_blank" rel="noopener noreferrer" className="font-medium text-indigo-600 hover:text-indigo-500">iArtHIS_lab</a> - Universidad de Málaga
               </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
