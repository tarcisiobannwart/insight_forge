"""
JavaScript/TypeScript Parser Module
----------------------------------
Parses JavaScript and TypeScript files using Node.js-based tools via subprocess.
"""

import os
import re
import json
import tempfile
import subprocess
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path

from .code_parser import CodeClass, CodeMethod


class NodeJsError(Exception):
    """Exception raised when Node.js is not available or has an error."""
    pass


class JsParseError(Exception):
    """Exception raised when JavaScript/TypeScript parsing fails."""
    pass


def check_nodejs_available() -> bool:
    """
    Check if Node.js is available in the system.
    
    Returns:
        True if Node.js is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["node", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False,
            timeout=2  # 2 second timeout
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def check_npm_available() -> bool:
    """
    Check if npm is available in the system.
    
    Returns:
        True if npm is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["npm", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            check=False,
            timeout=2  # 2 second timeout
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_parser_if_needed() -> bool:
    """
    Install required Node.js packages for parsing if they're not already installed.
    
    Returns:
        True if installation succeeded or packages already exist, False otherwise
    """
    # Check if the required tools are already installed
    parser_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parser_js")
    node_modules = os.path.join(parser_dir, "node_modules")
    package_json = os.path.join(parser_dir, "package.json")
    parser_js = os.path.join(parser_dir, "parser.js")
    
    # Create the directory if it doesn't exist
    os.makedirs(parser_dir, exist_ok=True)
    
    # Create package.json if it doesn't exist
    if not os.path.exists(package_json):
        with open(package_json, 'w', encoding='utf-8') as f:
            json.dump({
                "name": "insightforge-js-parser",
                "version": "1.0.0",
                "description": "JavaScript/TypeScript parser for InsightForge",
                "main": "parser.js",
                "dependencies": {
                    "@babel/parser": "^7.22.5",
                    "@babel/traverse": "^7.22.5",
                    "@babel/types": "^7.22.5",
                    "typescript": "^5.1.3",
                    "comment-parser": "^1.4.0"
                }
            }, f, indent=2)
    
    # Create parser.js if it doesn't exist
    if not os.path.exists(parser_js):
        with open(parser_js, 'w', encoding='utf-8') as f:
            f.write("""
const fs = require('fs');
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;
const t = require('@babel/types');
const commentParser = require('comment-parser');

// Parse a file and return the AST
function parseFile(filename, isTypeScript = false) {
    const code = fs.readFileSync(filename, 'utf-8');
    return parseCode(code, isTypeScript, filename);
}

// Parse code string and return the AST
function parseCode(code, isTypeScript = false, filename = 'unknown') {
    try {
        const plugins = [
            'jsx',
            'doExpressions',
            'objectRestSpread',
            'classProperties',
            'exportDefaultFrom',
            'exportNamespaceFrom',
            'asyncGenerators',
            'functionBind',
            'functionSent',
            'dynamicImport',
            'optionalChaining',
            'nullishCoalescingOperator',
        ];
        
        if (isTypeScript) {
            plugins.push('typescript');
            plugins.push('decorators-legacy');
        } else {
            plugins.push('flow');
        }
        
        const ast = parser.parse(code, {
            sourceType: 'module',
            plugins: plugins,
            ranges: true,
            locations: true,
            tokens: true,
            attachComment: true,
        });
        
        // Process and attach additional metadata
        const result = processAST(ast, code, filename);
        
        // Return JSON string
        return JSON.stringify(result);
    } catch (error) {
        throw new Error(`Error parsing ${isTypeScript ? 'TypeScript' : 'JavaScript'}: ${error.message}`);
    }
}

// Process the AST to extract classes, functions, etc.
function processAST(ast, code, filename) {
    const result = {
        classes: [],
        functions: [],
        imports: [],
        exports: [],
        comments: [],
        file_path: filename
    };
    
    // Process comments first
    if (ast.comments && ast.comments.length > 0) {
        ast.comments.forEach(comment => {
            if (comment.type === 'CommentBlock' && comment.value.startsWith('*')) {
                try {
                    // Parse JSDoc/TSDoc comments
                    const parsedComment = commentParser.parse('/*' + comment.value + '*/');
                    if (parsedComment && parsedComment.length > 0) {
                        result.comments.push({
                            type: 'jsdoc',
                            location: comment.loc,
                            value: comment.value,
                            parsed: parsedComment[0]
                        });
                    }
                } catch (e) {
                    // Just store the raw comment if parsing fails
                    result.comments.push({
                        type: 'block',
                        location: comment.loc,
                        value: comment.value
                    });
                }
            } else {
                result.comments.push({
                    type: comment.type === 'CommentBlock' ? 'block' : 'line',
                    location: comment.loc,
                    value: comment.value
                });
            }
        });
    }
    
    // Visit the AST to extract classes, functions, etc.
    traverse(ast, {
        // Handle class declarations
        ClassDeclaration(path) {
            const node = path.node;
            const classInfo = {
                type: 'class',
                name: node.id ? node.id.name : 'AnonymousClass',
                location: node.loc,
                superClass: node.superClass ? 
                    (node.superClass.type === 'Identifier' ? node.superClass.name : null) : 
                    null,
                implements: [], // Will be filled for TypeScript
                decorators: node.decorators ? node.decorators.map(d => {
                    return {
                        name: d.expression.type === 'Identifier' ? 
                            d.expression.name : 
                            (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                d.expression.callee.name : 
                                'unknown')
                    };
                }) : [],
                methods: [],
                properties: [],
                isAbstract: false, // Will be set for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            
            // Process class methods
            node.body.body.forEach(member => {
                if (t.isClassMethod(member) || t.isClassPrivateMethod(member)) {
                    const methodInfo = {
                        name: t.isClassMethod(member) ? 
                            (member.key.type === 'Identifier' ? member.key.name : 
                             (member.key.type === 'StringLiteral' ? member.key.value : 'unknown')) : 
                            member.key.id.name,
                        location: member.loc,
                        isStatic: member.static,
                        isPrivate: t.isClassPrivateMethod(member) || member.accessibility === 'private',
                        isAbstract: false, // Will be set for TypeScript
                        kind: member.kind, // 'constructor', 'method', 'get', 'set'
                        parameters: member.params.map(param => {
                            if (param.type === 'Identifier') {
                                return { name: param.name, default: null, type: null };
                            } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                                return { 
                                    name: param.left.name, 
                                    default: code.substring(param.right.start, param.right.end),
                                    type: null
                                };
                            }
                            return { name: 'unknown', default: null, type: null };
                        }),
                        returnType: null, // Will be filled for TypeScript
                        decorators: member.decorators ? member.decorators.map(d => {
                            return {
                                name: d.expression.type === 'Identifier' ? 
                                    d.expression.name : 
                                    (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                        d.expression.callee.name : 
                                        'unknown')
                            };
                        }) : [],
                        docstring: getDocComment(member, result.comments)
                    };
                    classInfo.methods.push(methodInfo);
                } 
                else if (t.isClassProperty(member) || t.isClassPrivateProperty(member)) {
                    const propInfo = {
                        name: t.isClassProperty(member) ? 
                            (member.key.type === 'Identifier' ? member.key.name : 
                             (member.key.type === 'StringLiteral' ? member.key.value : 'unknown')) : 
                            member.key.id.name,
                        location: member.loc,
                        isStatic: member.static,
                        isPrivate: t.isClassPrivateProperty(member) || member.accessibility === 'private',
                        isReadonly: false, // Will be set for TypeScript
                        type: null, // Will be filled for TypeScript
                        value: member.value ? code.substring(member.value.start, member.value.end) : null,
                        decorators: member.decorators ? member.decorators.map(d => {
                            return {
                                name: d.expression.type === 'Identifier' ? 
                                    d.expression.name : 
                                    (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                        d.expression.callee.name : 
                                        'unknown')
                            };
                        }) : [],
                        docstring: getDocComment(member, result.comments)
                    };
                    classInfo.properties.push(propInfo);
                }
            });
            
            result.classes.push(classInfo);
        },
        
        // Handle class expressions (e.g., const MyClass = class {...})
        ClassExpression(path) {
            const node = path.node;
            const parent = path.parent;
            let className = node.id ? node.id.name : 'AnonymousClass';
            
            // Try to get name from assignment if class is anonymous
            if (!node.id && parent && parent.type === 'VariableDeclarator' && parent.id.type === 'Identifier') {
                className = parent.id.name;
            }
            
            const classInfo = {
                type: 'class',
                name: className,
                location: node.loc,
                superClass: node.superClass ? 
                    (node.superClass.type === 'Identifier' ? node.superClass.name : null) : 
                    null,
                implements: [], // Will be filled for TypeScript
                decorators: node.decorators ? node.decorators.map(d => {
                    return {
                        name: d.expression.type === 'Identifier' ? 
                            d.expression.name : 
                            (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                d.expression.callee.name : 
                                'unknown')
                    };
                }) : [],
                methods: [],
                properties: [],
                isAbstract: false, // Will be set for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            
            // Process class methods and properties (same as class declaration)
            node.body.body.forEach(member => {
                if (t.isClassMethod(member) || t.isClassPrivateMethod(member)) {
                    const methodInfo = {
                        name: t.isClassMethod(member) ? 
                            (member.key.type === 'Identifier' ? member.key.name : 
                             (member.key.type === 'StringLiteral' ? member.key.value : 'unknown')) : 
                            member.key.id.name,
                        location: member.loc,
                        isStatic: member.static,
                        isPrivate: t.isClassPrivateMethod(member) || member.accessibility === 'private',
                        isAbstract: false, // Will be set for TypeScript
                        kind: member.kind, // 'constructor', 'method', 'get', 'set'
                        parameters: member.params.map(param => {
                            if (param.type === 'Identifier') {
                                return { name: param.name, default: null, type: null };
                            } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                                return { 
                                    name: param.left.name, 
                                    default: code.substring(param.right.start, param.right.end),
                                    type: null
                                };
                            }
                            return { name: 'unknown', default: null, type: null };
                        }),
                        returnType: null, // Will be filled for TypeScript
                        decorators: member.decorators ? member.decorators.map(d => {
                            return {
                                name: d.expression.type === 'Identifier' ? 
                                    d.expression.name : 
                                    (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                        d.expression.callee.name : 
                                        'unknown')
                            };
                        }) : [],
                        docstring: getDocComment(member, result.comments)
                    };
                    classInfo.methods.push(methodInfo);
                } 
                else if (t.isClassProperty(member) || t.isClassPrivateProperty(member)) {
                    const propInfo = {
                        name: t.isClassProperty(member) ? 
                            (member.key.type === 'Identifier' ? member.key.name : 
                             (member.key.type === 'StringLiteral' ? member.key.value : 'unknown')) : 
                            member.key.id.name,
                        location: member.loc,
                        isStatic: member.static,
                        isPrivate: t.isClassPrivateProperty(member) || member.accessibility === 'private',
                        isReadonly: false, // Will be set for TypeScript
                        type: null, // Will be filled for TypeScript
                        value: member.value ? code.substring(member.value.start, member.value.end) : null,
                        decorators: member.decorators ? member.decorators.map(d => {
                            return {
                                name: d.expression.type === 'Identifier' ? 
                                    d.expression.name : 
                                    (d.expression.type === 'CallExpression' && d.expression.callee.type === 'Identifier' ? 
                                        d.expression.callee.name : 
                                        'unknown')
                            };
                        }) : [],
                        docstring: getDocComment(member, result.comments)
                    };
                    classInfo.properties.push(propInfo);
                }
            });
            
            result.classes.push(classInfo);
        },
        
        // Handle function declarations
        FunctionDeclaration(path) {
            const node = path.node;
            const funcInfo = {
                type: 'function',
                name: node.id ? node.id.name : 'anonymousFunction',
                location: node.loc,
                isAsync: node.async,
                isGenerator: node.generator,
                parameters: node.params.map(param => {
                    if (param.type === 'Identifier') {
                        return { name: param.name, default: null, type: null };
                    } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                        return { 
                            name: param.left.name, 
                            default: code.substring(param.right.start, param.right.end),
                            type: null
                        };
                    }
                    return { name: 'unknown', default: null, type: null };
                }),
                returnType: null, // Will be filled for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            result.functions.push(funcInfo);
        },
        
        // Handle function expressions and arrow functions
        FunctionExpression(path) {
            const node = path.node;
            const parent = path.parent;
            let funcName = node.id ? node.id.name : 'anonymousFunction';
            
            // Try to get name from assignment or property
            if (!node.id) {
                if (parent.type === 'VariableDeclarator' && parent.id.type === 'Identifier') {
                    funcName = parent.id.name;
                } else if (parent.type === 'AssignmentExpression' && parent.left.type === 'Identifier') {
                    funcName = parent.left.name;
                } else if (parent.type === 'Property' && parent.key.type === 'Identifier') {
                    funcName = parent.key.name;
                } else if (parent.type === 'MethodDefinition' && parent.key.type === 'Identifier') {
                    funcName = parent.key.name;
                }
            }
            
            const funcInfo = {
                type: 'function',
                name: funcName,
                location: node.loc,
                isAsync: node.async,
                isGenerator: node.generator,
                parameters: node.params.map(param => {
                    if (param.type === 'Identifier') {
                        return { name: param.name, default: null, type: null };
                    } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                        return { 
                            name: param.left.name, 
                            default: code.substring(param.right.start, param.right.end),
                            type: null
                        };
                    }
                    return { name: 'unknown', default: null, type: null };
                }),
                returnType: null, // Will be filled for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            
            // Only add standalone functions, not methods (which are handled separately)
            if (parent.type !== 'MethodDefinition' && parent.type !== 'ClassMethod' && parent.type !== 'ObjectMethod') {
                result.functions.push(funcInfo);
            }
        },
        
        // Handle arrow functions
        ArrowFunctionExpression(path) {
            const node = path.node;
            const parent = path.parent;
            let funcName = 'arrowFunction';
            
            // Try to get name from assignment
            if (parent.type === 'VariableDeclarator' && parent.id.type === 'Identifier') {
                funcName = parent.id.name;
            } else if (parent.type === 'AssignmentExpression' && parent.left.type === 'Identifier') {
                funcName = parent.left.name;
            } else if (parent.type === 'Property' && parent.key.type === 'Identifier') {
                funcName = parent.key.name;
            }
            
            const funcInfo = {
                type: 'arrow_function',
                name: funcName,
                location: node.loc,
                isAsync: node.async,
                parameters: node.params.map(param => {
                    if (param.type === 'Identifier') {
                        return { name: param.name, default: null, type: null };
                    } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                        return { 
                            name: param.left.name, 
                            default: code.substring(param.right.start, param.right.end),
                            type: null
                        };
                    }
                    return { name: 'unknown', default: null, type: null };
                }),
                returnType: null, // Will be filled for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            
            // Only add standalone functions, not methods or small callbacks
            const isStandalone = (
                parent.type === 'VariableDeclarator' || 
                parent.type === 'AssignmentExpression' ||
                (parent.type === 'Property' && parent.method === false)
            );
            
            if (isStandalone) {
                result.functions.push(funcInfo);
            }
        },
        
        // Handle object method definitions
        ObjectMethod(path) {
            const node = path.node;
            const parent = path.parent;
            let objName = 'anonymous';
            
            // Try to get object name for context
            let currentPath = path.parentPath;
            while (currentPath && objName === 'anonymous') {
                if (currentPath.node.type === 'VariableDeclarator' && currentPath.node.id.type === 'Identifier') {
                    objName = currentPath.node.id.name;
                    break;
                } else if (currentPath.node.type === 'AssignmentExpression' && currentPath.node.left.type === 'Identifier') {
                    objName = currentPath.node.left.name;
                    break;
                }
                currentPath = currentPath.parentPath;
            }
            
            const methodName = node.key.type === 'Identifier' ? 
                node.key.name : 
                (node.key.type === 'StringLiteral' ? node.key.value : 'unknownMethod');
            
            const funcInfo = {
                type: 'object_method',
                name: methodName,
                object: objName,
                location: node.loc,
                isAsync: node.async,
                isGenerator: node.generator,
                kind: node.kind, // 'method', 'get', or 'set'
                parameters: node.params.map(param => {
                    if (param.type === 'Identifier') {
                        return { name: param.name, default: null, type: null };
                    } else if (param.type === 'AssignmentPattern' && param.left.type === 'Identifier') {
                        return { 
                            name: param.left.name, 
                            default: code.substring(param.right.start, param.right.end),
                            type: null
                        };
                    }
                    return { name: 'unknown', default: null, type: null };
                }),
                returnType: null, // Will be filled for TypeScript
                docstring: getDocComment(node, result.comments)
            };
            
            result.functions.push(funcInfo);
        },
        
        // Handle imports
        ImportDeclaration(path) {
            const node = path.node;
            const importInfo = {
                type: 'import',
                source: node.source.value,
                location: node.loc,
                specifiers: node.specifiers.map(specifier => {
                    if (specifier.type === 'ImportDefaultSpecifier') {
                        return { type: 'default', local: specifier.local.name };
                    } else if (specifier.type === 'ImportNamespaceSpecifier') {
                        return { type: 'namespace', local: specifier.local.name };
                    } else if (specifier.type === 'ImportSpecifier') {
                        return { 
                            type: 'named', 
                            local: specifier.local.name, 
                            imported: specifier.imported.name 
                        };
                    }
                })
            };
            result.imports.push(importInfo);
        },
        
        // Handle exports
        ExportNamedDeclaration(path) {
            const node = path.node;
            const exportInfo = {
                type: 'named_export',
                location: node.loc,
                source: node.source ? node.source.value : null,
                specifiers: node.specifiers.map(specifier => {
                    return { 
                        local: specifier.local.name, 
                        exported: specifier.exported.name 
                    };
                }),
                declaration: node.declaration ? {
                    type: node.declaration.type
                } : null
            };
            result.exports.push(exportInfo);
        },
        
        ExportDefaultDeclaration(path) {
            const node = path.node;
            const exportInfo = {
                type: 'default_export',
                location: node.loc,
                declaration: {
                    type: node.declaration.type,
                    name: node.declaration.type === 'Identifier' ? node.declaration.name : null
                }
            };
            result.exports.push(exportInfo);
        },
        
        // Handle TypeScript interfaces (if parsing TypeScript)
        TSInterfaceDeclaration(path) {
            const node = path.node;
            const interfaceInfo = {
                type: 'interface',
                name: node.id.name,
                location: node.loc,
                extends: node.extends ? node.extends.map(ext => {
                    return ext.expression.type === 'Identifier' ? ext.expression.name : 'unknown';
                }) : [],
                properties: [],
                methods: [],
                docstring: getDocComment(node, result.comments)
            };
            
            // Process interface properties and methods
            if (node.body && node.body.body) {
                node.body.body.forEach(member => {
                    if (member.type === 'TSPropertySignature') {
                        interfaceInfo.properties.push({
                            name: member.key.type === 'Identifier' ? member.key.name : 'unknown',
                            location: member.loc,
                            isReadonly: !!member.readonly,
                            isOptional: !!member.optional,
                            type: member.typeAnnotation ? 
                                code.substring(member.typeAnnotation.start, member.typeAnnotation.end) : 
                                'any',
                            docstring: getDocComment(member, result.comments)
                        });
                    } else if (member.type === 'TSMethodSignature') {
                        interfaceInfo.methods.push({
                            name: member.key.type === 'Identifier' ? member.key.name : 'unknown',
                            location: member.loc,
                            isOptional: !!member.optional,
                            parameters: member.parameters ? member.parameters.map(param => {
                                return {
                                    name: param.type === 'Identifier' ? param.name : 'unknown',
                                    isOptional: !!param.optional,
                                    type: param.typeAnnotation ? 
                                        code.substring(param.typeAnnotation.start, param.typeAnnotation.end) : 
                                        'any'
                                };
                            }) : [],
                            returnType: member.typeAnnotation ? 
                                code.substring(member.typeAnnotation.start, member.typeAnnotation.end) : 
                                'any',
                            docstring: getDocComment(member, result.comments)
                        });
                    }
                });
            }
            
            result.classes.push(interfaceInfo);
        },
        
        // Handle TypeScript type aliases
        TSTypeAliasDeclaration(path) {
            const node = path.node;
            const typeInfo = {
                type: 'type_alias',
                name: node.id.name,
                location: node.loc,
                aliasType: code.substring(node.typeAnnotation.start, node.typeAnnotation.end),
                docstring: getDocComment(node, result.comments)
            };
            result.exports.push(typeInfo);
        },
        
        // Handle TypeScript enums
        TSEnumDeclaration(path) {
            const node = path.node;
            const enumInfo = {
                type: 'enum',
                name: node.id.name,
                location: node.loc,
                members: node.members.map(member => {
                    return {
                        name: member.id.type === 'Identifier' ? member.id.name : 
                            (member.id.type === 'StringLiteral' ? member.id.value : 'unknown'),
                        value: member.initializer ? 
                            code.substring(member.initializer.start, member.initializer.end) : 
                            null
                    };
                }),
                docstring: getDocComment(node, result.comments)
            };
            result.classes.push(enumInfo);
        }
    });
    
    return result;
}

// Get the associated JSDoc comment for a node
function getDocComment(node, comments) {
    if (!comments || comments.length === 0 || !node.loc) {
        return null;
    }
    
    // Find the closest comment above the node
    const nodeStart = node.loc.start.line;
    let closestComment = null;
    let closestDistance = Infinity;
    
    for (const comment of comments) {
        if (comment.location && comment.location.end.line < nodeStart) {
            const distance = nodeStart - comment.location.end.line;
            if (distance < closestDistance && distance <= 3) { // Max 3 lines distance
                closestDistance = distance;
                closestComment = comment;
            }
        }
    }
    
    return closestComment;
}

// Main entry point for CLI usage
function main() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.error("Usage: node parser.js <filename> [--typescript]");
        process.exit(1);
    }
    
    const filename = args[0];
    const isTypeScript = args.includes('--typescript');
    
    try {
        const result = parseFile(filename, isTypeScript);
        console.log(result);
    } catch (error) {
        console.error(error.message);
        process.exit(1);
    }
}

// If called directly
if (require.main === module) {
    main();
} else {
    // Export for use as a module
    module.exports = {
        parseFile,
        parseCode
    };
}
            """)
    
    # If node_modules doesn't exist, install the dependencies
    if not os.path.exists(node_modules):
        if not check_nodejs_available() or not check_npm_available():
            logging.warning("Node.js or npm not available. JS/TS parsing will be disabled.")
            return False
        
        try:
            logging.info("Installing JavaScript parser dependencies (this may take a moment)...")
            subprocess.run(
                ["npm", "install"], 
                cwd=parser_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logging.info("JavaScript parser dependencies installed successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to install JavaScript parser dependencies: {e}")
            return False
    
    return True


class JsNode:
    """Base class for JavaScript AST nodes."""
    
    def __init__(self, node_data: Dict[str, Any], file_path: str):
        """
        Initialize the JS node.
        
        Args:
            node_data: Node data from the AST
            file_path: Path to the file containing the node
        """
        self.node_data = node_data
        self.file_path = file_path
        self.name = node_data.get('name', 'Unknown')
        self.docstring = self._extract_docstring()
        self.line_number = self._get_line_number()
    
    def _extract_docstring(self) -> Optional[str]:
        """Extract docstring from the node."""
        doc_node = self.node_data.get('docstring')
        if not doc_node:
            return None
        
        if isinstance(doc_node, str):
            return doc_node
        
        # For parsed JSDoc comments
        if doc_node.get('type') == 'jsdoc':
            parsed = doc_node.get('parsed')
            if parsed:
                # Extract description and tags
                description = parsed.get('description', '')
                tags = []
                
                for tag in parsed.get('tags', []):
                    tag_name = tag.get('tag')
                    tag_desc = tag.get('description', '')
                    tag_type = tag.get('type', '')
                    tag_name = tag.get('name', '')
                    
                    if tag_name and tag_desc:
                        tags.append(f"@{tag_name} {tag_name} {tag_type} {tag_desc}")
                    elif tag_name:
                        tags.append(f"@{tag_name} {tag_type} {tag_desc}")
                
                if tags:
                    return description + '\n\n' + '\n'.join(tags)
                return description
        
        # Fallback to raw comment value
        return doc_node.get('value', '')
    
    def _get_line_number(self) -> int:
        """Get the line number of the node."""
        location = self.node_data.get('location')
        if location and location.get('start') and location['start'].get('line'):
            return location['start']['line']
        return 0


class JsClass(JsNode):
    """Represents a JavaScript/TypeScript class."""
    
    def __init__(self, class_data: Dict[str, Any], file_path: str):
        """
        Initialize the JS class.
        
        Args:
            class_data: Class data from the AST
            file_path: Path to the file containing the class
        """
        super().__init__(class_data, file_path)
        self.is_interface = class_data.get('type') == 'interface'
        self.is_enum = class_data.get('type') == 'enum'
        self.extends = class_data.get('superClass', []) or []
        if not isinstance(self.extends, list):
            self.extends = [self.extends] if self.extends else []
        
        self.implements = class_data.get('implements', [])
        if not isinstance(self.implements, list):
            self.implements = [self.implements] if self.implements else []
        
        self.methods = self._extract_methods()
        self.properties = class_data.get('properties', [])
        self.decorators = class_data.get('decorators', [])
        self.is_abstract = class_data.get('isAbstract', False)
    
    def _extract_methods(self) -> List[Dict[str, Any]]:
        """Extract methods from the class data."""
        methods = []
        for method_data in self.node_data.get('methods', []):
            method = {
                'name': method_data.get('name', 'unknown'),
                'docstring': self._extract_method_docstring(method_data),
                'line_number': self._get_method_line_number(method_data),
                'parameters': [p.get('name', 'unknown') for p in method_data.get('parameters', [])],
                'return_type': method_data.get('returnType'),
                'is_static': method_data.get('isStatic', False),
                'is_abstract': method_data.get('isAbstract', False),
                'is_private': method_data.get('isPrivate', False),
                'kind': method_data.get('kind', 'method')
            }
            methods.append(method)
        
        return methods
    
    def _extract_method_docstring(self, method_data: Dict[str, Any]) -> Optional[str]:
        """Extract docstring from a method."""
        doc_node = method_data.get('docstring')
        if not doc_node:
            return None
        
        if isinstance(doc_node, str):
            return doc_node
        
        # For parsed JSDoc comments
        if doc_node.get('type') == 'jsdoc':
            parsed = doc_node.get('parsed')
            if parsed:
                # Extract description and tags
                description = parsed.get('description', '')
                tags = []
                
                for tag in parsed.get('tags', []):
                    tag_name = tag.get('tag')
                    tag_desc = tag.get('description', '')
                    tag_type = tag.get('type', '')
                    tag_name = tag.get('name', '')
                    
                    if tag_name and tag_desc:
                        tags.append(f"@{tag_name} {tag_name} {tag_type} {tag_desc}")
                    elif tag_name:
                        tags.append(f"@{tag_name} {tag_type} {tag_desc}")
                
                if tags:
                    return description + '\n\n' + '\n'.join(tags)
                return description
        
        # Fallback to raw comment value
        return doc_node.get('value', '')
    
    def _get_method_line_number(self, method_data: Dict[str, Any]) -> int:
        """Get the line number of a method."""
        location = method_data.get('location')
        if location and location.get('start') and location['start'].get('line'):
            return location['start']['line']
        return 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'is_interface': self.is_interface,
            'is_enum': self.is_enum,
            'extends': self.extends,
            'implements': self.implements,
            'methods': self.methods,
            'properties': self.properties,
            'decorators': self.decorators,
            'is_abstract': self.is_abstract
        }


class JsFunction(JsNode):
    """Represents a JavaScript/TypeScript function."""
    
    def __init__(self, function_data: Dict[str, Any], file_path: str):
        """
        Initialize the JS function.
        
        Args:
            function_data: Function data from the AST
            file_path: Path to the file containing the function
        """
        super().__init__(function_data, file_path)
        self.parameters = [p.get('name', 'unknown') for p in function_data.get('parameters', [])]
        self.return_type = function_data.get('returnType')
        self.is_async = function_data.get('isAsync', False)
        self.is_generator = function_data.get('isGenerator', False)
        self.is_arrow = function_data.get('type') == 'arrow_function'
        self.is_method = function_data.get('type') == 'object_method'
        self.object_name = function_data.get('object') if self.is_method else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'docstring': self.docstring,
            'line_number': self.line_number,
            'file_path': self.file_path,
            'parameters': self.parameters,
            'return_type': self.return_type,
            'is_async': self.is_async,
            'is_generator': self.is_generator,
            'is_arrow': self.is_arrow,
            'is_method': self.is_method,
            'object_name': self.object_name
        }


class JavaScriptParser:
    """
    Parser for JavaScript/TypeScript files using Node.js.
    
    Requires Node.js and npm to be installed on the system.
    """
    
    def __init__(self, file_path: str = None):
        """
        Initialize the JavaScript parser.
        
        Args:
            file_path: Path to the JavaScript file to parse
        """
        self.file_path = file_path
        self.is_typescript = file_path and file_path.endswith(('.ts', '.tsx')) if file_path else False
        self.nodejs_available = check_nodejs_available() and check_npm_available()
        self.parser_installed = False
        
        # Install parser dependencies if needed
        if self.nodejs_available:
            self.parser_installed = install_parser_if_needed()
        
        self.logger = logging.getLogger(__name__)
    
    def parse(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Parse the JavaScript file to extract classes and functions.
        
        Returns:
            Tuple of (classes, functions, metadata) as dictionaries
        """
        if not self.file_path:
            return [], [], {}
        
        if not self.nodejs_available or not self.parser_installed:
            self.logger.warning("Node.js or npm not available, or parser not installed. JavaScript parsing disabled.")
            return [], [], {}
        
        try:
            # Get the parser script path
            parser_js = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), 
                "parser_js", 
                "parser.js"
            )
            
            # Run parser script with Node.js
            cmd = ["node", parser_js, self.file_path]
            if self.is_typescript:
                cmd.append("--typescript")
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            
            # Parse the output JSON
            parsed_data = json.loads(result.stdout)
            
            # Process classes and functions
            classes = []
            functions = []
            
            # Convert classes
            for class_data in parsed_data.get('classes', []):
                js_class = JsClass(class_data, self.file_path)
                classes.append(js_class.to_dict())
            
            # Convert functions
            for function_data in parsed_data.get('functions', []):
                js_function = JsFunction(function_data, self.file_path)
                functions.append(js_function.to_dict())
            
            # Gather metadata
            metadata = {
                'imports': parsed_data.get('imports', []),
                'exports': parsed_data.get('exports', []),
                'comments': parsed_data.get('comments', []),
                'is_typescript': self.is_typescript,
                'file_path': self.file_path
            }
            
            return classes, functions, metadata
            
        except (subprocess.SubprocessError, json.JSONDecodeError) as e:
            self.logger.error(f"Error parsing JavaScript file {self.file_path}: {str(e)}")
            return [], [], {}
        except Exception as e:
            self.logger.error(f"Unexpected error parsing JavaScript file {self.file_path}: {str(e)}")
            return [], [], {}


class JavaScriptProjectParser:
    """Parser for JavaScript/TypeScript projects."""
    
    def __init__(
        self,
        project_dir: str,
        exclude_dirs: List[str] = None,
        file_extensions: List[str] = None
    ):
        """
        Initialize the JavaScript project parser.
        
        Args:
            project_dir: Root directory of the project
            exclude_dirs: Directories to exclude from parsing
            file_extensions: File extensions to include
        """
        self.project_dir = project_dir
        self.exclude_dirs = exclude_dirs or ['node_modules', 'dist', 'build', 'coverage', '.git']
        self.file_extensions = file_extensions or ['.js', '.jsx', '.ts', '.tsx']
        self.logger = logging.getLogger(__name__)
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the JavaScript project.
        
        Returns:
            Dictionary with parsed data
        """
        all_classes = []
        all_functions = []
        all_imports = []
        all_exports = []
        file_dependencies = {}
        
        # Find JavaScript files
        js_files = self._find_js_files()
        
        # Parse each file
        for file_path in js_files:
            self.logger.debug(f"Parsing JavaScript file: {file_path}")
            
            parser = JavaScriptParser(file_path)
            classes, functions, metadata = parser.parse()
            
            # Add to collections
            all_classes.extend(classes)
            all_functions.extend(functions)
            all_imports.extend(metadata.get('imports', []))
            all_exports.extend(metadata.get('exports', []))
            
            # Build file dependencies based on imports
            rel_path = os.path.relpath(file_path, self.project_dir)
            file_dependencies[rel_path] = []
            
            for imp in metadata.get('imports', []):
                source = imp.get('source')
                if source:
                    if source.startswith('.'):
                        # Relative import
                        source_path = os.path.normpath(
                            os.path.join(os.path.dirname(file_path), source)
                        )
                        if not source.endswith(tuple(self.file_extensions)):
                            # Try to find the actual file
                            for ext in self.file_extensions:
                                if os.path.exists(source_path + ext):
                                    source_path += ext
                                    break
                                elif os.path.exists(os.path.join(source_path, 'index' + ext)):
                                    source_path = os.path.join(source_path, 'index' + ext)
                                    break
                        
                        if os.path.exists(source_path):
                            rel_source = os.path.relpath(source_path, self.project_dir)
                            file_dependencies[rel_path].append(rel_source)
            
        return {
            'classes': all_classes,
            'functions': all_functions,
            'imports': all_imports,
            'exports': all_exports,
            'file_dependencies': file_dependencies
        }
    
    def _find_js_files(self) -> List[str]:
        """
        Find all JavaScript/TypeScript files in the project.
        
        Returns:
            List of paths to JavaScript files
        """
        js_files = []
        
        for root, dirs, files in os.walk(self.project_dir):
            # Remove excluded directories
            for exclude_dir in self.exclude_dirs:
                if exclude_dir in dirs:
                    dirs.remove(exclude_dir)
            
            # Add JavaScript files
            for file in files:
                if file.endswith(tuple(self.file_extensions)):
                    js_files.append(os.path.join(root, file))
        
        return js_files


def adapt_js_to_insightforge(parsed_js_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Adapt JavaScript/TypeScript parsed data to InsightForge format.
    
    Args:
        parsed_js_data: Data parsed by JavaScriptProjectParser
        
    Returns:
        Data in InsightForge format
    """
    insightforge_classes = []
    
    # Convert JavaScript classes to InsightForge format
    for js_class in parsed_js_data.get('classes', []):
        # Create methods list
        methods = []
        for method in js_class.get('methods', []):
            code_method = CodeMethod(
                name=method['name'],
                docstring=method.get('docstring', ''),
                line_number=method.get('line_number', 0),
                parameters=method.get('parameters', []),
                file_path=js_class.get('file_path', ''),
                class_name=js_class['name'],
                return_type=method.get('return_type')
            )
            methods.append(code_method)
        
        # Create code class
        code_class = CodeClass(
            name=js_class['name'],
            docstring=js_class.get('docstring', ''),
            methods=methods,
            line_number=js_class.get('line_number', 0),
            file_path=js_class.get('file_path', '')
        )
        
        # Add base classes
        code_class.base_classes = js_class.get('extends', [])
        code_class.base_classes.extend(js_class.get('implements', []))
        
        # Add properties as attributes
        for prop in js_class.get('properties', []):
            code_class.attributes.append({
                'name': prop['name'],
                'type': prop.get('type'),
                'is_class_var': prop.get('isStatic', False),
                'line_number': prop.get('line_number', 0),
                'docstring': prop.get('docstring', ''),
                'visibility': 'private' if prop.get('isPrivate', False) else 'public'
            })
        
        # Add metadata for interface or enum
        if js_class.get('is_interface'):
            code_class.attributes.append({
                'name': '__type__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': 'This is a TypeScript interface',
                'visibility': 'public'
            })
        elif js_class.get('is_enum'):
            code_class.attributes.append({
                'name': '__type__',
                'type': 'metadata',
                'is_class_var': True,
                'line_number': 0,
                'docstring': 'This is a TypeScript enum',
                'visibility': 'public'
            })
        
        # Add to collection
        insightforge_classes.append(code_class.to_dict())
    
    # Convert JavaScript functions to InsightForge format
    insightforge_functions = []
    for js_function in parsed_js_data.get('functions', []):
        func_dict = {
            'name': js_function['name'],
            'docstring': js_function.get('docstring', ''),
            'line_number': js_function.get('line_number', 0),
            'file_path': js_function.get('file_path', ''),
            'parameters': js_function.get('parameters', []),
            'return_type': js_function.get('return_type')
        }
        
        # Add metadata for async, generator, arrow
        metadata = []
        if js_function.get('is_async'):
            metadata.append('async')
        if js_function.get('is_generator'):
            metadata.append('generator')
        if js_function.get('is_arrow'):
            metadata.append('arrow function')
        if js_function.get('is_method'):
            metadata.append(f"method of {js_function.get('object_name', 'unknown')}")
        
        if metadata:
            func_dict['metadata'] = ', '.join(metadata)
            
        insightforge_functions.append(func_dict)
    
    # Create a dependency mapping from imports
    file_deps = parsed_js_data.get('file_dependencies', {})
    dependencies = []
    
    # Add file dependencies
    for source_file, target_files in file_deps.items():
        for target in target_files:
            dependencies.append({
                'source': source_file,
                'target': target,
                'type': 'import'
            })
    
    # Return in InsightForge format
    return {
        'classes': insightforge_classes,
        'functions': insightforge_functions,
        'modules': [],  # JavaScript doesn't have modules like Python
        'dependencies': dependencies
    }