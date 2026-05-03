'use client';

import React, { useState } from 'react';

export default function HashIdentifier() {
    const [inputHash, setInputHash] = useState<string>('');
    const [identifiedTypes, setIdentifiedTypes] = useState<string[]>([]);

    const identifyHash = (hash: string): string[] => {
        const types: string[] = [];

        // 1. Check for Modular Crypt Format (MCF) Prefixes
        if (hash.startsWith('$1$')) types.push('MD5 Crypt');
        if (hash.match(/^\$2[aby]\$/)) types.push('bcrypt');
        if (hash.startsWith('$5$')) types.push('SHA-256 Crypt');
        if (hash.startsWith('$6$')) types.push('SHA-512 Crypt');
        if (hash.startsWith('$argon2i$') || hash.startsWith('$argon2id$')) {
            types.push('Argon2');
        }

        // 2. Check for Raw Hashes (Hexadecimal) if no MCF prefix is found
        if (types.length === 0 && /^[a-fA-F0-9]+$/.test(hash)) {
            const length = hash.length;

            switch (length) {
                case 32:
                    types.push('Raw MD5 (or MD4, NTLM)');
                    break;
                case 40:
                    types.push('Raw SHA-1');
                    break;
                case 64:
                    types.push('Raw SHA-256');
                    break;
                case 128:
                    types.push('Raw SHA-512');
                    break;
                default:
                    types.push('Unknown Hexadecimal String');
            }
        }

        // 3. Fallback
        if (types.length === 0) {
            types.push('Unknown Format');
        }

        return types;
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value.trim();
        setInputHash(value);
        if (value) {
            setIdentifiedTypes(identifyHash(value));
        } else {
            setIdentifiedTypes([]);
        }
    };

    return (
        <div className="p-6 max-w-lg mx-auto bg-gray-50 rounded-xl shadow-md mt-10 text-black">
            <h2 className="text-xl font-bold mb-4">Hash Identification Tool</h2>

            <label className="block mb-2 font-medium text-gray-700">
                Paste Hash String:
            </label>
            <input
                type="text"
                value={inputHash}
                onChange={handleInputChange}
                className="w-full p-2 border border-gray-300 rounded mb-4 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., $2y$10$..."
            />

            {inputHash && (
                <div className="bg-white p-4 border border-gray-200 rounded">
                    <h3 className="font-semibold text-gray-800 mb-2">Possible Types:</h3>
                    <ul className="list-disc pl-5">
                        {identifiedTypes.map((type, index) => (
                            <li key={index} className="text-gray-600">{type}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}