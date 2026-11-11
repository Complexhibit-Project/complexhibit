import { Suspense } from "react";
import type { Metadata } from "next";
import GraphExplorer from "@/components/graph/GraphExplorer";

export const metadata: Metadata = {
  title: "Knowledge Graph Explorer · Complexhibit",
  description:
    "Interactively explore the OntoExhibit knowledge graph: traverse exhibitions, artworks, people and institutions through their semantic relationships.",
};

export default function GraphPage() {
  return (
    <Suspense fallback={null}>
      <GraphExplorer />
    </Suspense>
  );
}
