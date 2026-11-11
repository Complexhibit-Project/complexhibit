"use client";

/**
 * Dependency-free force-directed graph renderer (SVG + a small physics loop).
 *
 * Built from scratch so the platform ships no extra graph library: nodes repel
 * each other, edges act as springs, and a weak centring force keeps the layout
 * on screen. Supports drag, pan and zoom, and surfaces click / expand events.
 *
 * The simulation reads live data/size from refs so a single stable animation
 * loop always operates on the latest graph (important when nodes are added by
 * expansion).
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { GraphData, GraphNode } from "@/lib/graph";
import { nodeColor } from "@/lib/graph";

interface SimNode {
  x: number;
  y: number;
  vx: number;
  vy: number;
  fixed: boolean;
}

interface ForceGraphProps {
  data: GraphData;
  selectedId?: string | null;
  onNodeClick?: (node: GraphNode) => void;
  onNodeDoubleClick?: (node: GraphNode) => void;
  height?: number;
  className?: string;
}

const REPULSION = 9000;
const SPRING_LENGTH = 90;
const SPRING_STRENGTH = 0.04;
const CENTER_GRAVITY = 0.02;
const DAMPING = 0.82;
const MIN_ALPHA = 0.01;

export default function ForceGraph({
  data,
  selectedId,
  onNodeClick,
  onNodeDoubleClick,
  height = 560,
  className = "",
}: ForceGraphProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const sim = useRef<Map<string, SimNode>>(new Map());
  const alpha = useRef(1);
  const raf = useRef<number | null>(null);
  const [size, setSize] = useState({ w: 800, h: height });
  const [, setTick] = useState(0);
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const [hovered, setHovered] = useState<string | null>(null);

  // Live refs so the stable animation loop always sees current data/size.
  const dataRef = useRef(data);
  dataRef.current = data;
  const sizeRef = useRef(size);
  sizeRef.current = size;

  const dragNode = useRef<string | null>(null);
  const panning = useRef<{ x: number; y: number } | null>(null);
  const moved = useRef(false);

  const step = useCallback(() => {
    const nodes = dataRef.current.nodes;
    const edges = dataRef.current.edges;
    const cx = sizeRef.current.w / 2;
    const cy = sizeRef.current.h / 2;
    const a = alpha.current;

    for (let i = 0; i < nodes.length; i++) {
      const ni = sim.current.get(nodes[i].id);
      if (!ni) continue;
      for (let j = i + 1; j < nodes.length; j++) {
        const nj = sim.current.get(nodes[j].id);
        if (!nj) continue;
        let dx = ni.x - nj.x;
        let dy = ni.y - nj.y;
        let dist2 = dx * dx + dy * dy;
        if (dist2 < 1) {
          dx = Math.random() - 0.5;
          dy = Math.random() - 0.5;
          dist2 = 1;
        }
        const dist = Math.sqrt(dist2);
        const force = (REPULSION / dist2) * a;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        ni.vx += fx;
        ni.vy += fy;
        nj.vx -= fx;
        nj.vy -= fy;
      }
    }

    for (const e of edges) {
      const s = sim.current.get(e.source);
      const t = sim.current.get(e.target);
      if (!s || !t) continue;
      const dx = t.x - s.x;
      const dy = t.y - s.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = (dist - SPRING_LENGTH) * SPRING_STRENGTH * a;
      const fx = (dx / dist) * force;
      const fy = (dy / dist) * force;
      s.vx += fx;
      s.vy += fy;
      t.vx -= fx;
      t.vy -= fy;
    }

    for (const n of nodes) {
      const sn = sim.current.get(n.id);
      if (!sn) continue;
      if (sn.fixed) {
        sn.vx = 0;
        sn.vy = 0;
        continue;
      }
      sn.vx += (cx - sn.x) * CENTER_GRAVITY * a;
      sn.vy += (cy - sn.y) * CENTER_GRAVITY * a;
      sn.vx *= DAMPING;
      sn.vy *= DAMPING;
      sn.x += sn.vx;
      sn.y += sn.vy;
    }

    alpha.current = Math.max(0, a * 0.985);
  }, []);

  const startLoop = useCallback(() => {
    if (raf.current != null) return;
    const tickLoop = () => {
      step();
      setTick((t) => t + 1);
      if (alpha.current > MIN_ALPHA || dragNode.current) {
        raf.current = requestAnimationFrame(tickLoop);
      } else {
        raf.current = null;
      }
    };
    raf.current = requestAnimationFrame(tickLoop);
  }, [step]);

  const reheat = useCallback(
    (value = 1) => {
      alpha.current = Math.max(alpha.current, value);
      startLoop();
    },
    [startLoop],
  );

  // Measure the container.
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const update = () => setSize({ w: el.clientWidth, h: height });
    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    return () => ro.disconnect();
  }, [height]);

  // Sync simulation node set with incoming data; seed new nodes near the centre.
  useEffect(() => {
    const cx = sizeRef.current.w / 2;
    const cy = sizeRef.current.h / 2;
    const present = new Set<string>();
    data.nodes.forEach((n, i) => {
      present.add(n.id);
      if (!sim.current.has(n.id)) {
        const angle = (i / Math.max(1, data.nodes.length)) * Math.PI * 2;
        const radius = n.isFocus ? 0 : 60 + Math.random() * 120;
        sim.current.set(n.id, {
          x: cx + Math.cos(angle) * radius,
          y: cy + Math.sin(angle) * radius,
          vx: 0,
          vy: 0,
          fixed: false,
        });
      }
    });
    for (const id of Array.from(sim.current.keys())) {
      if (!present.has(id)) sim.current.delete(id);
    }
    reheat(1);
  }, [data, reheat]);

  useEffect(() => {
    return () => {
      if (raf.current != null) cancelAnimationFrame(raf.current);
    };
  }, []);

  // --- pointer helpers -------------------------------------------------
  const toGraph = (clientX: number, clientY: number) => {
    const rect = containerRef.current?.getBoundingClientRect();
    const px = clientX - (rect?.left ?? 0);
    const py = clientY - (rect?.top ?? 0);
    return { x: (px - transform.x) / transform.k, y: (py - transform.y) / transform.k };
  };

  const releaseDrag = () => {
    if (dragNode.current) {
      const sn = sim.current.get(dragNode.current);
      if (sn) sn.fixed = false;
    }
    dragNode.current = null;
    panning.current = null;
  };

  const onPointerDownNode = (e: React.PointerEvent, id: string) => {
    e.stopPropagation();
    (e.target as Element).setPointerCapture?.(e.pointerId);
    dragNode.current = id;
    moved.current = false;
    const sn = sim.current.get(id);
    if (sn) sn.fixed = true;
    startLoop();
  };

  const onPointerMove = (e: React.PointerEvent) => {
    if (dragNode.current) {
      const sn = sim.current.get(dragNode.current);
      if (sn) {
        const p = toGraph(e.clientX, e.clientY);
        sn.x = p.x;
        sn.y = p.y;
        moved.current = true;
      }
      reheat(0.4);
    } else if (panning.current) {
      // Capture the delta now: the setState updater runs later, by which point
      // releaseDrag may have set panning.current to null.
      const dx = e.clientX - panning.current.x;
      const dy = e.clientY - panning.current.y;
      panning.current = { x: e.clientX, y: e.clientY };
      setTransform((tf) => ({ ...tf, x: tf.x + dx, y: tf.y + dy }));
    }
  };

  const onPointerDownBg = (e: React.PointerEvent) => {
    panning.current = { x: e.clientX, y: e.clientY };
  };

  const onWheel = (e: React.WheelEvent) => {
    const rect = containerRef.current?.getBoundingClientRect();
    const px = e.clientX - (rect?.left ?? 0);
    const py = e.clientY - (rect?.top ?? 0);
    const factor = e.deltaY < 0 ? 1.1 : 1 / 1.1;
    setTransform((tf) => {
      const k = Math.min(3, Math.max(0.2, tf.k * factor));
      return {
        k,
        x: px - (px - tf.x) * (k / tf.k),
        y: py - (py - tf.y) * (k / tf.k),
      };
    });
  };

  const adjacency = useMemo(() => {
    const map = new Map<string, Set<string>>();
    for (const e of data.edges) {
      if (!map.has(e.source)) map.set(e.source, new Set());
      if (!map.has(e.target)) map.set(e.target, new Set());
      map.get(e.source)!.add(e.target);
      map.get(e.target)!.add(e.source);
    }
    return map;
  }, [data.edges]);

  const focusId = useMemo(() => data.nodes.find((n) => n.isFocus)?.id ?? null, [data.nodes]);

  // Per-edge perpendicular offset so parallel / bidirectional edges between the
  // same pair fan out into separate curves instead of stacking their labels.
  const edgeOffsets = useMemo(() => {
    const groups = new Map<string, number[]>();
    data.edges.forEach((e, i) => {
      const key = e.source < e.target ? `${e.source}|${e.target}` : `${e.target}|${e.source}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key)!.push(i);
    });
    const offsets = new Array(data.edges.length).fill(0);
    groups.forEach((idxs) => {
      const m = idxs.length;
      idxs.forEach((edgeIdx, j) => {
        offsets[edgeIdx] = j - (m - 1) / 2;
      });
    });
    return offsets;
  }, [data.edges]);

  const isDimmed = (id: string) => {
    if (!hovered) return false;
    if (id === hovered) return false;
    return !adjacency.get(hovered)?.has(id);
  };

  // By default surface the relationships of the active node (hovered → selected →
  // focus). Only show every label at once for small graphs.
  const activeNode = hovered ?? selectedId ?? focusId;
  const showAllLabels = data.edges.length <= 18;

  return (
    <div
      ref={containerRef}
      className={`relative overflow-hidden rounded-2xl bg-slate-50 ${className}`}
      style={{ height }}
    >
      <svg
        width={size.w}
        height={size.h}
        className="touch-none select-none"
        style={{ cursor: "grab" }}
        onPointerDown={onPointerDownBg}
        onPointerMove={onPointerMove}
        onPointerUp={releaseDrag}
        onPointerLeave={releaseDrag}
        onWheel={onWheel}
      >
        <defs>
          <marker
            id="fg-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="6"
            markerHeight="6"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="#cbd5e1" />
          </marker>
        </defs>
        <g transform={`translate(${transform.x},${transform.y}) scale(${transform.k})`}>
          {/* Edges */}
          {data.edges.map((e, i) => {
            const s = sim.current.get(e.source);
            const t = sim.current.get(e.target);
            if (!s || !t) return null;
            const incidentHover = !!hovered && (e.source === hovered || e.target === hovered);
            const incidentActive = !!activeNode && (e.source === activeNode || e.target === activeNode);
            const dim = !!hovered && !incidentHover;

            const dx = t.x - s.x;
            const dy = t.y - s.y;
            const len = Math.hypot(dx, dy) || 1;
            const nx = -dy / len; // unit perpendicular
            const ny = dx / len;
            const off = edgeOffsets[i] * 18;
            const cx = (s.x + t.x) / 2 + nx * off * 2; // bezier control point
            const cy = (s.y + t.y) / 2 + ny * off * 2;
            const lx = (s.x + t.x) / 2 + nx * off; // label sits on the curve
            const ly = (s.y + t.y) / 2 + ny * off;
            const stroke = incidentHover ? "#6366f1" : "#d1d5db";
            const sw = incidentHover ? 1.8 : 1;

            return (
              <g key={`e-${i}`} opacity={dim ? 0.1 : 1}>
                {off === 0 ? (
                  <line x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke={stroke} strokeWidth={sw} markerEnd="url(#fg-arrow)" />
                ) : (
                  <path
                    d={`M ${s.x} ${s.y} Q ${cx} ${cy} ${t.x} ${t.y}`}
                    fill="none"
                    stroke={stroke}
                    strokeWidth={sw}
                    markerEnd="url(#fg-arrow)"
                  />
                )}
                {(incidentActive || showAllLabels) && (
                  <EdgeLabel x={lx} y={ly} text={e.label} active={incidentHover} />
                )}
              </g>
            );
          })}

          {/* Nodes */}
          {data.nodes.map((n) => {
            const sn = sim.current.get(n.id);
            if (!sn) return null;
            const selected = selectedId === n.id;
            const dim = isDimmed(n.id);
            const commonHandlers = {
              onPointerDown: (e: React.PointerEvent) => onPointerDownNode(e, n.id),
              onPointerUp: (e: React.PointerEvent) => {
                e.stopPropagation();
                const wasMoved = moved.current;
                releaseDrag();
                if (!wasMoved) onNodeClick?.(n);
              },
              onDoubleClick: (e: React.MouseEvent) => {
                e.stopPropagation();
                onNodeDoubleClick?.(n);
              },
              onMouseEnter: () => setHovered(n.id),
              onMouseLeave: () => setHovered((h) => (h === n.id ? null : h)),
            };

            // Literal (data-property) node → a small rounded pill showing the value.
            if (n.kind === "literal") {
              const text = truncate(n.label, 22);
              const w = text.length * 5.4 + 14;
              return (
                <g
                  key={n.id}
                  transform={`translate(${sn.x},${sn.y})`}
                  opacity={dim ? 0.25 : 1}
                  style={{ cursor: "pointer" }}
                  {...commonHandlers}
                >
                  <rect
                    x={-w / 2}
                    y={-9}
                    width={w}
                    height={18}
                    rx={5}
                    fill="#f1f5f9"
                    stroke={selected ? "#1e293b" : "#cbd5e1"}
                    strokeWidth={selected ? 2 : 1}
                    strokeDasharray="3 2"
                  />
                  <text textAnchor="middle" dy={3.5} className="pointer-events-none" fontSize={9} fill="#475569">
                    {text}
                  </text>
                </g>
              );
            }

            const color = nodeColor(n.type);
            const r = n.isFocus ? 13 : 9;
            return (
              <g
                key={n.id}
                transform={`translate(${sn.x},${sn.y})`}
                opacity={dim ? 0.25 : 1}
                style={{ cursor: "pointer" }}
                {...commonHandlers}
              >
                <circle
                  r={r}
                  fill={color}
                  stroke={selected ? "#1e293b" : "#ffffff"}
                  strokeWidth={selected ? 3 : 2}
                />
                {n.isFocus && <circle r={r + 4} fill="none" stroke={color} strokeWidth={1.5} opacity={0.5} />}
                {!n.expanded && !n.isFocus && (
                  <circle r={2.5} cx={r - 2} cy={-(r - 2)} fill="#fff" stroke={color} strokeWidth={1} />
                )}
                <text
                  y={r + 11}
                  textAnchor="middle"
                  className="pointer-events-none"
                  fontSize={n.isFocus ? 11 : 9.5}
                  fontWeight={n.isFocus ? 700 : 500}
                  fill="#0f172a"
                >
                  {truncate(n.label, 26)}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
}

function truncate(s: string, max: number): string {
  if (!s) return "";
  return s.length > max ? `${s.slice(0, max - 1)}…` : s;
}

/** Edge label with a readable pill background so it stays legible over lines. */
function EdgeLabel({ x, y, text, active }: { x: number; y: number; text: string; active: boolean }) {
  const width = text.length * 5.2 + 8;
  return (
    <g transform={`translate(${x},${y})`} className="pointer-events-none">
      <rect x={-width / 2} y={-7} width={width} height={13} rx={3} fill="#ffffff" opacity={active ? 0.95 : 0.8} />
      <text
        textAnchor="middle"
        dy={2.5}
        fontSize={8.5}
        fontWeight={active ? 600 : 500}
        fill={active ? "#4338ca" : "#6b7280"}
      >
        {text}
      </text>
    </g>
  );
}
