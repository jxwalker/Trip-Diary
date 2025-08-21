"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Save, 
  RotateCcw, 
  Globe, 
  ChevronLeft,
  FileText,
  Sparkles,
  Map,
  Utensils,
  Calendar,
  Info,
  AlertTriangle,
  Check,
  Copy,
  Eye,
  EyeOff,
  Code,
  Lightbulb,
  Settings,
  BookOpen
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

interface PromptSection {
  id: string;
  title: string;
  description: string;
  icon: any;
  prompts: {
    [key: string]: {
      template?: string;
      description?: string;
      context_required?: string[];
      output_format?: any;
      max_length?: number;
    };
  };
}

export default function PromptEditorPage() {
  const router = useRouter();
  const [prompts, setPrompts] = useState<any>(null);
  const [originalPrompts, setOriginalPrompts] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [selectedSection, setSelectedSection] = useState("travel_guide");
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/proxy/prompts");
      
      if (!response.ok) {
        throw new Error("Failed to fetch prompts");
      }
      
      const data = await response.json();
      setPrompts(data);
      setOriginalPrompts(JSON.parse(JSON.stringify(data))); // Deep copy
      setLoading(false);
    } catch (err) {
      console.error("Error fetching prompts:", err);
      setErrorMessage("Failed to load prompts. Please try again.");
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setSavedMessage("");
      setErrorMessage("");
      
      const response = await fetch("/api/proxy/prompts", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(prompts),
      });
      
      if (!response.ok) {
        throw new Error("Failed to save prompts");
      }
      
      setOriginalPrompts(JSON.parse(JSON.stringify(prompts)));
      setUnsavedChanges(false);
      setSavedMessage("Prompts saved successfully!");
      
      // Clear message after 3 seconds
      setTimeout(() => setSavedMessage(""), 3000);
    } catch (err) {
      console.error("Error saving prompts:", err);
      setErrorMessage("Failed to save prompts. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    if (window.confirm("Are you sure you want to discard all changes?")) {
      setPrompts(JSON.parse(JSON.stringify(originalPrompts)));
      setUnsavedChanges(false);
    }
  };

  const handlePromptChange = (section: string, component: string, field: string, value: string) => {
    setPrompts((prev: any) => {
      const updated = { ...prev };
      if (!updated[section]) updated[section] = {};
      if (!updated[section].components) updated[section].components = {};
      if (!updated[section].components[component]) updated[section].components[component] = {};
      updated[section].components[component][field] = value;
      return updated;
    });
    setUnsavedChanges(true);
  };

  const handleBasePromptChange = (section: string, value: string) => {
    setPrompts((prev: any) => {
      const updated = { ...prev };
      if (!updated[section]) updated[section] = {};
      updated[section].base_prompt = value;
      return updated;
    });
    setUnsavedChanges(true);
  };

  const sections: PromptSection[] = [
    {
      id: "travel_guide",
      title: "Travel Guide",
      description: "Main prompts for generating personalized travel guides",
      icon: Map,
      prompts: prompts?.travel_guide?.components || {}
    },
    {
      id: "itinerary_extraction",
      title: "Itinerary Extraction",
      description: "Prompts for extracting travel information from documents",
      icon: FileText,
      prompts: prompts?.itinerary_extraction?.components || {}
    },
    {
      id: "search_queries",
      title: "Search Queries",
      description: "Templates for web search queries",
      icon: Globe,
      prompts: prompts?.search_queries?.components || {}
    },
    {
      id: "output_formats",
      title: "Output Formats",
      description: "Structure definitions for different outputs",
      icon: Code,
      prompts: prompts?.output_formats || {}
    }
  ];

  const getComponentTitle = (key: string) => {
    return key.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
        <div className="container mx-auto px-6 py-24 flex items-center justify-center">
          <Card className="w-full max-w-md">
            <CardContent className="pt-6">
              <div className="text-center space-y-4">
                <Settings className="h-12 w-12 text-sky-500 mx-auto animate-spin" />
                <h3 className="text-xl font-semibold">Loading Prompt Editor</h3>
                <p className="text-gray-500">Please wait...</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-sky-50">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <div className="flex items-center space-x-2">
              <Settings className="h-6 w-6 text-sky-500" />
              <span className="text-xl font-bold bg-gradient-to-r from-sky-500 to-blue-600 bg-clip-text text-transparent">
                Prompt Editor
              </span>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {unsavedChanges && (
              <Badge variant="outline" className="bg-yellow-50 border-yellow-300">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Unsaved Changes
              </Badge>
            )}
            <Button
              onClick={() => setShowPreview(!showPreview)}
              variant="outline"
              size="sm"
            >
              {showPreview ? (
                <>
                  <EyeOff className="h-4 w-4 mr-2" />
                  Hide Preview
                </>
              ) : (
                <>
                  <Eye className="h-4 w-4 mr-2" />
                  Show Preview
                </>
              )}
            </Button>
            <Button
              onClick={handleReset}
              variant="outline"
              size="sm"
              disabled={!unsavedChanges}
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
            <Button
              onClick={handleSave}
              className="bg-gradient-to-r from-sky-500 to-blue-600"
              size="sm"
              disabled={saving || !unsavedChanges}
            >
              {saving ? (
                <>
                  <Settings className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </nav>

      <div className="pt-24 pb-12 px-6">
        <div className="container mx-auto max-w-7xl">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <Badge className="mb-4 px-4 py-1 bg-gradient-to-r from-sky-500 to-blue-600">
              <Sparkles className="h-3 w-3 mr-1" />
              AI Prompt Configuration
            </Badge>
            <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-gray-900 to-sky-600 bg-clip-text text-transparent">
              Customize AI Prompts
            </h1>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Fine-tune the AI prompts to generate better travel guides and recommendations.
              Changes will affect how the AI processes and generates content.
            </p>
          </motion.div>

          {/* Alerts */}
          {savedMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <Alert className="bg-green-50 border-green-200">
                <Check className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  {savedMessage}
                </AlertDescription>
              </Alert>
            </motion.div>
          )}

          {errorMessage && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6"
            >
              <Alert className="bg-red-50 border-red-200">
                <AlertTriangle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">
                  {errorMessage}
                </AlertDescription>
              </Alert>
            </motion.div>
          )}

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Section Selector */}
            <div className="lg:col-span-1">
              <Card>
                <CardHeader>
                  <CardTitle>Prompt Sections</CardTitle>
                  <CardDescription>
                    Select a section to edit its prompts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {sections.map((section) => {
                      const Icon = section.icon;
                      return (
                        <Button
                          key={section.id}
                          onClick={() => setSelectedSection(section.id)}
                          variant={selectedSection === section.id ? "default" : "outline"}
                          className="w-full justify-start"
                        >
                          <Icon className="h-4 w-4 mr-2" />
                          {section.title}
                        </Button>
                      );
                    })}
                  </div>

                  <div className="mt-6 p-4 bg-sky-50 rounded-lg">
                    <h4 className="font-medium text-sm mb-2 flex items-center">
                      <Lightbulb className="h-4 w-4 mr-2 text-sky-600" />
                      Tips for Better Prompts
                    </h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      <li>• Be specific about desired output format</li>
                      <li>• Include context variables like {"{destination}"}</li>
                      <li>• Use clear, actionable language</li>
                      <li>• Specify any constraints or requirements</li>
                      <li>• Test changes with sample data</li>
                    </ul>
                  </div>

                  <div className="mt-6 p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-medium text-sm mb-2 flex items-center">
                      <BookOpen className="h-4 w-4 mr-2 text-purple-600" />
                      Available Variables
                    </h4>
                    <div className="text-xs text-gray-600 space-y-1">
                      <code className="block bg-white p-1 rounded">{"{destination}"}</code>
                      <code className="block bg-white p-1 rounded">{"{start_date}"}</code>
                      <code className="block bg-white p-1 rounded">{"{end_date}"}</code>
                      <code className="block bg-white p-1 rounded">{"{preferences_summary}"}</code>
                      <code className="block bg-white p-1 rounded">{"{hotel_info}"}</code>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Prompt Editor */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    {sections.find(s => s.id === selectedSection)?.icon && (
                      <div className="mr-2">
                        {(() => {
                          const Icon = sections.find(s => s.id === selectedSection)?.icon;
                          return Icon ? <Icon className="h-5 w-5 text-sky-500" /> : null;
                        })()}
                      </div>
                    )}
                    {sections.find(s => s.id === selectedSection)?.title}
                  </CardTitle>
                  <CardDescription>
                    {sections.find(s => s.id === selectedSection)?.description}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[600px] pr-4">
                    <div className="space-y-6">
                      {/* Base Prompt */}
                      {prompts?.[selectedSection]?.base_prompt && (
                        <div>
                          <Label htmlFor="base_prompt" className="text-base font-medium mb-2">
                            Base Prompt
                          </Label>
                          <p className="text-sm text-gray-500 mb-2">
                            The main instruction that guides the AI's behavior for this section
                          </p>
                          <Textarea
                            id="base_prompt"
                            value={prompts[selectedSection].base_prompt}
                            onChange={(e) => handleBasePromptChange(selectedSection, e.target.value)}
                            className="font-mono text-sm"
                            rows={8}
                          />
                        </div>
                      )}

                      {/* Component Prompts */}
                      {prompts?.[selectedSection]?.components && 
                        Object.entries(prompts[selectedSection].components).map(([key, component]: [string, any]) => (
                          <div key={key} className="border rounded-lg p-4 bg-gray-50">
                            <h3 className="font-medium mb-3 flex items-center">
                              <Code className="h-4 w-4 mr-2 text-gray-500" />
                              {getComponentTitle(key)}
                            </h3>
                            
                            {component.description && (
                              <p className="text-sm text-gray-600 mb-3">
                                {component.description}
                              </p>
                            )}

                            {component.template && (
                              <div className="space-y-2">
                                <Label htmlFor={`${key}_template`} className="text-sm">
                                  Template
                                </Label>
                                <Textarea
                                  id={`${key}_template`}
                                  value={component.template}
                                  onChange={(e) => handlePromptChange(selectedSection, key, "template", e.target.value)}
                                  className="font-mono text-xs"
                                  rows={6}
                                />
                              </div>
                            )}

                            {component.context_required && (
                              <div className="mt-3">
                                <Label className="text-sm">Required Context</Label>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {component.context_required.map((ctx: string) => (
                                    <Badge key={ctx} variant="outline" className="text-xs">
                                      {ctx}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            {component.max_length && (
                              <div className="mt-2">
                                <span className="text-xs text-gray-500">
                                  Max Length: {component.max_length} tokens
                                </span>
                              </div>
                            )}
                          </div>
                        ))
                      }

                      {/* Output Formats */}
                      {selectedSection === "output_formats" && prompts?.output_formats &&
                        Object.entries(prompts.output_formats).map(([key, format]: [string, any]) => (
                          <div key={key} className="border rounded-lg p-4 bg-gray-50">
                            <h3 className="font-medium mb-3">
                              {getComponentTitle(key)}
                            </h3>
                            <pre className="text-xs bg-white p-3 rounded overflow-x-auto">
                              {JSON.stringify(format, null, 2)}
                            </pre>
                          </div>
                        ))
                      }
                    </div>
                  </ScrollArea>

                  {/* Preview Panel */}
                  {showPreview && (
                    <div className="mt-6 p-4 border-2 border-dashed border-gray-300 rounded-lg">
                      <h4 className="font-medium mb-2 flex items-center">
                        <Eye className="h-4 w-4 mr-2" />
                        Preview
                      </h4>
                      <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                        <p className="mb-2">This is how your prompt will be sent to the AI:</p>
                        <pre className="whitespace-pre-wrap text-xs">
                          {prompts?.[selectedSection]?.base_prompt || "No base prompt defined"}
                        </pre>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Help Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-8"
          >
            <Card className="bg-gradient-to-r from-sky-50 to-blue-50">
              <CardContent className="pt-6">
                <div className="flex items-start space-x-4">
                  <Info className="h-8 w-8 text-sky-600 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-2">About Prompt Editing</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      These prompts control how the AI generates travel guides, extracts information from documents,
                      and provides recommendations. Changes here will affect the quality and style of AI-generated content.
                    </p>
                    <p className="text-sm text-gray-600">
                      <strong>Best Practices:</strong> Test your changes with sample data, be specific about output requirements,
                      and use context variables to make prompts dynamic. Remember to save your changes before leaving this page.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}