<script>
    let { userFingerprint, saveAnswer } = $props();

    // Demographics state - matches existing survey categories
    let demographics = $state({
        age: '',
        gender_ord: '',
        orientation_ord: '',
        race_ord: ''
    });

    // Save each field when changed
    async function handleChange(field, value) {
        demographics[field] = value;
        if (value !== '' && userFingerprint) {
            await saveAnswer(field, value);
        }
    }
</script>

<div class="demographics-box">
    <h3>Tell us about yourself <span class="optional">(optional)</span></h3>

    <div class="demo-grid">
        <div class="demo-field">
            <label for="age">Age</label>
            <select
                id="age"
                bind:value={demographics.age}
                onchange={() => handleChange('age', demographics.age)}>
                <option value="">Select...</option>
                <option value="18-24">18-24</option>
                <option value="25-34">25-34</option>
                <option value="35-44">35-44</option>
                <option value="45-54">45-54</option>
                <option value="55-64">55-64</option>
                <option value="65+">65+</option>
            </select>
        </div>

        <div class="demo-field">
            <label for="gender">Gender</label>
            <select
                id="gender"
                bind:value={demographics.gender_ord}
                onchange={() => handleChange('gender_ord', demographics.gender_ord)}>
                <option value="">Select...</option>
                <option value="0">Women</option>
                <option value="1">Men</option>
            </select>
        </div>

        <div class="demo-field">
            <label for="orientation">Sexual Orientation</label>
            <select
                id="orientation"
                bind:value={demographics.orientation_ord}
                onchange={() => handleChange('orientation_ord', demographics.orientation_ord)}>
                <option value="">Select...</option>
                <option value="0">Straight</option>
                <option value="1">Bisexual</option>
                <option value="2">Gay</option>
                <option value="3">Other</option>
            </select>
        </div>

        <div class="demo-field">
            <label for="race">Race/Ethnicity</label>
            <select
                id="race"
                bind:value={demographics.race_ord}
                onchange={() => handleChange('race_ord', demographics.race_ord)}>
                <option value="">Select...</option>
                <option value="0">White</option>
                <option value="1">Mixed</option>
                <option value="2">POC</option>
            </select>
        </div>
    </div>
</div>

<style>
    .demographics-box {
        max-width: 800px;
        margin: 2rem auto;
        margin-bottom: 75vh;
        padding: 2rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    h3 {
        margin: 0 0 1.5rem 0;
        font-size: 1.3rem;
        font-weight: 600;
        text-align: center;
        color: whitesmoke;
    }

    .optional {
        font-size: 0.9rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.6);
    }

    .demo-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 1.5rem;
    }

    .demo-field {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    label {
        font-size: 0.9rem;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.9);
    }

    select {
        padding: 0.6rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 6px;
        font-size: 0.95rem;
        background: rgba(0, 0, 0, 0.3);
        color: whitesmoke;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    select:hover {
        border-color: rgba(255, 255, 255, 0.4);
        background: rgba(0, 0, 0, 0.4);
    }

    select:focus {
        outline: none;
        border-color: #0891b2;
        box-shadow: 0 0 0 2px rgba(8, 145, 178, 0.2);
    }

    option {
        background: #1a1a1a;
        color: whitesmoke;
    }

    @media (max-width: 640px) {
        .demo-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
