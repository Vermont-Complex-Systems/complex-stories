import { institutionsByDemographic } from './institutions.js';

// Generate data with demographic-specific trust patterns
export const generatePeopleByInstitution = () => {
    const people = [];
    let personId = 0;

    // Generate data for each demographic group
    Object.keys(institutionsByDemographic).forEach(demographic => {
        const institutions = institutionsByDemographic[demographic];
        
        institutions.forEach(inst => {
            // Generate 8-12 people per institution to show variation
            const numPeople = Math.floor(Math.random() * 5) + 8; // 8-12 people
            
            for (let i = 0; i < numPeople; i++) {
                // Generate trustworthiness with normal distribution around average
                const randomVariation = (Math.random() - 0.5) * 2 * inst.variation;
                const trustworthiness = Math.max(1, Math.min(7, Math.round(inst.avgTrust + randomVariation)));
                
                // Extract gender and ethnicity from demographic key
                let gender, ethnicity;
                if (demographic === 'all') {
                    gender = ['men', 'women', 'nonbinary'][Math.floor(Math.random() * 3)];
                    ethnicity = ['white', 'black', 'asian'][Math.floor(Math.random() * 3)];
                } else {
                    const [eth, gen] = demographic.split('_');
                    ethnicity = eth;
                    gender = gen;
                }
                
                people.push({
                    id: personId++,
                    institution: inst.name,
                    label: inst.label,
                    trustworthiness: trustworthiness,
                    gender: gender,
                    ethnicity: ethnicity,
                    demographic: demographic
                });
            }
        });
    });

    return people;
};