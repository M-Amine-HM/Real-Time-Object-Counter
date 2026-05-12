import React from "react";

export default function StatCard({ label, value }) {
    return (
        <div className="stat-card">
            <p className="stat-label">{label}</p>
            <p className="stat-value">{value}</p>
        </div>
    );
}
