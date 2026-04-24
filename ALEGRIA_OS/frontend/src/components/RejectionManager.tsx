/*
 * -------------------------------------------------------------------------
 * ALEGR-IA OS — Sistema Operativo de Coherencia Creativa
 * Copyright (c) 2025 Sebastián Fernández & Antigravity AI.
 * Todos los derechos reservados.
 *
 * Este código es CONFIDENCIAL y PROPIETARIO.
 * Su copia, distribución o modificación no autorizada está penada por la ley.
 * -------------------------------------------------------------------------
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Plus, Trash2, Edit2, Eye, EyeOff, Save, X,
    AlertCircle, CheckCircle, Shield, Info
} from 'lucide-react';

const API_URL = import.meta.env.DEV ? '/api' : `http://${window.location.hostname}:8000`;

interface Rejection {
    id: string;
    type: string;
    description: string;
    severity: string;
    active: boolean;
    created_at: string;
    updated_at?: string;
}

interface RejectionType {
    value: string;
    label: string;
    description: string;
}

interface Severity {
    value: string;
    label: string;
    description: string;
}

const RejectionManager: React.FC = () => {
    const [rejections, setRejections] = useState<Rejection[]>([]);
    const [types, setTypes] = useState<RejectionType[]>([]);
    const [severities, setSeverities] = useState<Severity[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [showPreview, setShowPreview] = useState(false);
    const [previewPrompt, setPreviewPrompt] = useState('');

    // Form state
    const [formData, setFormData] = useState({
        type: 'topic',
        description: '',
        severity: 'moderate',
        active: true
    });

    useEffect(() => {
        loadRejections();
        loadMetadata();
    }, []);

    const loadRejections = async () => {
        try {
            setLoading(true);
            const response = await axios.get(`${API_URL}/api/rejections`);
            setRejections(response.data);
            setError(null);
        } catch (err: any) {
            setError('Error cargando rechazos: ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    const loadMetadata = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/rejections/types`);
            setTypes(response.data.types);
            setSeverities(response.data.severities);
        } catch (err) {
            console.error('Error loading metadata:', err);
        }
    };

    const loadPreview = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/rejections/preview/prompt`);
            setPreviewPrompt(response.data.prompt || 'No hay rechazos activos');
            setShowPreview(true);
        } catch (err) {
            console.error('Error loading preview:', err);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            if (editingId) {
                // Update existing rejection
                await axios.put(`${API_URL}/api/rejections/${editingId}`, formData);
            } else {
                // Create new rejection
                await axios.post(`${API_URL}/api/rejections`, formData);
            }

            await loadRejections();
            resetForm();
        } catch (err: any) {
            setError('Error guardando rechazo: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleEdit = (rejection: Rejection) => {
        setFormData({
            type: rejection.type,
            description: rejection.description,
            severity: rejection.severity,
            active: rejection.active
        });
        setEditingId(rejection.id);
        setShowForm(true);
    };

    const handleDelete = async (id: string) => {
        if (!confirm('¿Estás seguro de eliminar este rechazo?')) return;

        try {
            await axios.delete(`${API_URL}/api/rejections/${id}`);
            await loadRejections();
        } catch (err: any) {
            setError('Error eliminando rechazo: ' + (err.response?.data?.detail || err.message));
        }
    };

    const handleToggleActive = async (rejection: Rejection) => {
        try {
            await axios.put(`${API_URL}/api/rejections/${rejection.id}`, {
                active: !rejection.active
            });
            await loadRejections();
        } catch (err: any) {
            setError('Error actualizando rechazo: ' + (err.response?.data?.detail || err.message));
        }
    };

    const resetForm = () => {
        setFormData({
            type: 'topic',
            description: '',
            severity: 'moderate',
            active: true
        });
        setEditingId(null);
        setShowForm(false);
    };

    const getTypeEmoji = (type: string) => {
        const emojiMap: Record<string, string> = {
            topic: '📚',
            behavior: '🎭',
            style: '✍️',
            content: '📝',
            language: '🗣️'
        };
        return emojiMap[type] || '❌';
    };

    const getSeverityColor = (severity: string) => {
        const colorMap: Record<string, string> = {
            strict: 'bg-red-500/20 border-red-500/50 text-red-300',
            moderate: 'bg-yellow-500/20 border-yellow-500/50 text-yellow-300',
            soft: 'bg-blue-500/20 border-blue-500/50 text-blue-300'
        };
        return colorMap[severity] || 'bg-gray-500/20 border-gray-500/50 text-gray-300';
    };

    const getSeverityIcon = (severity: string) => {
        if (severity === 'strict') return <Shield className="w-4 h-4" />;
        if (severity === 'moderate') return <AlertCircle className="w-4 h-4" />;
        return <Info className="w-4 h-4" />;
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-full">
                <div className="text-slate-400">Cargando rechazos...</div>
            </div>
        );
    }

    return (
        <div className="h-full flex flex-col bg-transparent text-slate-200 p-6 overflow-hidden">
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-3xl font-bold mb-2 text-glow text-white">Sistema de Rechazos de Usuario</h1>
                <p className="text-slate-400">
                    Define explícitamente qué contenido, temas o comportamientos Anima debe evitar
                </p>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="mb-4 p-4 bg-red-500/10 border border-red-500/50 rounded-lg flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                        <p className="text-red-300">{error}</p>
                        <button
                            onClick={() => setError(null)}
                            className="text-xs text-red-400 hover:text-red-300 mt-1"
                        >
                            Cerrar
                        </button>
                    </div>
                </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3 mb-6">
                <button
                    onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 px-4 py-2 bg-neon-violet hover:bg-violet-600 text-white rounded-lg transition-all shadow-[0_0_10px_rgba(139,92,246,0.3)] hover:shadow-[0_0_15px_rgba(139,92,246,0.5)]"
                >
                    {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                    {showForm ? 'Cancelar' : 'Nuevo Rechazo'}
                </button>

                <button
                    onClick={loadPreview}
                    className="flex items-center gap-2 px-4 py-2 glass-btn rounded-lg text-slate-300 hover:text-white"
                >
                    <Eye className="w-4 h-4" />
                    Vista Previa del Prompt
                </button>

                <div className="ml-auto flex items-center gap-2 text-sm text-slate-400">
                    <CheckCircle className="w-4 h-4 text-neon-emerald" />
                    {rejections.filter(r => r.active).length} rechazos activos
                </div>
            </div>

            {/* Form */}
            {showForm && (
                <div className="mb-6 p-6 glass-panel rounded-xl animate-fade-in">
                    <h3 className="text-lg font-semibold mb-4 text-white">
                        {editingId ? 'Editar Rechazo' : 'Nuevo Rechazo'}
                    </h3>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium mb-2 text-slate-300">Tipo de Rechazo</label>
                                <select
                                    value={formData.type}
                                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                    className="w-full px-3 py-2 bg-black/40 border border-glass-border rounded-lg focus:outline-none focus:border-neon-violet text-slate-200"
                                    title="Tipo de Rechazo"
                                >
                                    {types.map(type => (
                                        <option key={type.value} value={type.value} className="bg-slate-900">
                                            {getTypeEmoji(type.value)} {type.label} - {type.description}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-slate-300">Severidad</label>
                                <select
                                    value={formData.severity}
                                    onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                                    className="w-full px-3 py-2 bg-black/40 border border-glass-border rounded-lg focus:outline-none focus:border-neon-violet text-slate-200"
                                    title="Severidad"
                                >
                                    {severities.map(sev => (
                                        <option key={sev.value} value={sev.value} className="bg-slate-900">
                                            {sev.label} - {sev.description}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2 text-slate-300">Descripción del Rechazo</label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                placeholder="Ej: No hablar sobre política, No usar lenguaje técnico excesivo, Evitar temas controversiales..."
                                className="w-full px-3 py-2 bg-black/40 border border-glass-border rounded-lg focus:outline-none focus:border-neon-violet min-h-[100px] text-slate-200 placeholder-slate-600"
                                required
                                minLength={3}
                            />
                        </div>

                        <div className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                id="active"
                                checked={formData.active}
                                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                                className="w-4 h-4 rounded border-glass-border bg-black/40 text-neon-violet focus:ring-neon-violet"
                            />
                            <label htmlFor="active" className="text-sm text-slate-300">Rechazo activo</label>
                        </div>

                        <div className="flex gap-3 pt-2">
                            <button
                                type="submit"
                                className="flex items-center gap-2 px-4 py-2 bg-neon-violet hover:bg-violet-600 text-white rounded-lg transition-colors shadow-lg shadow-neon-violet/20"
                            >
                                <Save className="w-4 h-4" />
                                {editingId ? 'Actualizar' : 'Guardar'}
                            </button>

                            <button
                                type="button"
                                onClick={resetForm}
                                className="px-4 py-2 glass-btn rounded-lg text-slate-300 hover:text-white"
                            >
                                Cancelar
                            </button>
                        </div>
                    </form>
                </div>
            )}

            {/* Rejections List */}
            <div className="flex-1 overflow-y-auto space-y-3 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent pr-2">
                {rejections.length === 0 ? (
                    <div className="text-center py-12 text-slate-500">
                        <Shield className="w-12 h-12 mx-auto mb-3 opacity-30" />
                        <p>No hay rechazos configurados</p>
                        <p className="text-sm mt-1">Agrega rechazos para que Anima los respete en sus respuestas</p>
                    </div>
                ) : (
                    rejections.map(rejection => (
                        <div
                            key={rejection.id}
                            className={`p-4 rounded-lg border transition-all duration-300 ${rejection.active
                                ? 'bg-glass-light border-glass-border hover:bg-white/5'
                                : 'bg-black/20 border-white/5 opacity-60'
                                }`}
                        >
                            <div className="flex items-start gap-3">
                                <div className="text-2xl filter drop-shadow-md">{getTypeEmoji(rejection.type)}</div>

                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-sm font-medium text-slate-300 capitalize">
                                            {rejection.type}
                                        </span>
                                        <span className={`text-xs px-2 py-0.5 rounded-full border flex items-center gap-1 ${getSeverityColor(rejection.severity)}`}>
                                            {getSeverityIcon(rejection.severity)}
                                            {rejection.severity}
                                        </span>
                                    </div>

                                    <p className="text-slate-200 mb-2">{rejection.description}</p>

                                    <p className="text-xs text-slate-500">
                                        Creado: {new Date(rejection.created_at).toLocaleDateString('es-ES')}
                                    </p>
                                </div>

                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleToggleActive(rejection)}
                                        className={`p-2 rounded-lg transition-colors ${rejection.active
                                            ? 'bg-neon-emerald/10 text-neon-emerald hover:bg-neon-emerald/20'
                                            : 'bg-white/5 text-slate-500 hover:text-slate-300'
                                            }`}
                                        title={rejection.active ? 'Desactivar' : 'Activar'}
                                    >
                                        {rejection.active ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
                                    </button>

                                    <button
                                        onClick={() => handleEdit(rejection)}
                                        className="p-2 glass-btn rounded-lg text-slate-400 hover:text-white"
                                        title="Editar"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>

                                    <button
                                        onClick={() => handleDelete(rejection.id)}
                                        className="p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors border border-red-500/20"
                                        title="Eliminar"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Preview Modal */}
            {showPreview && (
                <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-6 animate-fade-in">
                    <div className="glass-panel rounded-xl max-w-3xl w-full max-h-[80vh] flex flex-col shadow-2xl shadow-neon-violet/10">
                        <div className="p-6 border-b border-glass-border flex items-center justify-between">
                            <h3 className="text-xl font-semibold text-white">Vista Previa del Prompt de Rechazos</h3>
                            <button
                                onClick={() => setShowPreview(false)}
                                className="p-2 hover:bg-white/10 rounded-lg transition-colors text-slate-400 hover:text-white"
                                title="Cerrar vista previa"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="p-6 overflow-y-auto flex-1">
                            <pre className="text-sm text-slate-300 whitespace-pre-wrap font-mono bg-black/50 p-4 rounded-lg border border-glass-border">
                                {previewPrompt}
                            </pre>
                        </div>

                        <div className="p-6 border-t border-glass-border">
                            <p className="text-sm text-slate-400">
                                Este prompt se incluye automáticamente en todas las conversaciones con Anima para garantizar que respete tus rechazos.
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RejectionManager;
