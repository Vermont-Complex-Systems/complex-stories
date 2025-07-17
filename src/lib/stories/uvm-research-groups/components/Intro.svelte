<script>
  import WaffleChart from './Waffle.svelte';
  import { group } from 'd3-array'
  import { base } from '$app/paths';

  let { data } = $props();
  
  let groupBy = $state('college'); // 'college' or 'host_dept'
  
  let groupedData = $derived(() => {
    if (!data?.length) return new Map();
    
    const flattenedData = data.flatMap(person => {
      const values = (person[groupBy] || 'Unknown').split(';').map(d => d.trim());
      return values.map(value => ({
        ...person,
        [groupBy]: value
      }));
    });
    
    const grouped = group(flattenedData, d => d[groupBy]);
    
    if (groupBy === 'host_dept') {
      // For departments, group by college
      const deptsByCollege = new Map();
      
      for (const [dept, people] of grouped) {
        // Get the most common college for this department
        const colleges = people.map(p => p.college || 'Unknown');
        const collegeCount = colleges.reduce((acc, college) => {
          acc[college] = (acc[college] || 0) + 1;
          return acc;
        }, {});
        const primaryCollege = Object.keys(collegeCount).reduce((a, b) => 
          collegeCount[a] > collegeCount[b] ? a : b
        );
        
        if (!deptsByCollege.has(primaryCollege)) {
          deptsByCollege.set(primaryCollege, []);
        }
        deptsByCollege.get(primaryCollege).push([dept, people]);
      }
      
      // Sort colleges and departments within each college
      const sortedColleges = Array.from(deptsByCollege.entries())
        .sort((a, b) => a[0].localeCompare(b[0]))
        .map(([college, depts]) => [
          college, 
          depts.sort((a, b) => b[1].length - a[1].length)
        ]);
      
      return sortedColleges;
    } else {
      // For colleges, just sort by size
      const sortedEntries = Array.from(grouped.entries())
        .sort((a, b) => b[1].length - a[1].length);
      
      return new Map(sortedEntries);
    }
  });
</script>


<section id="story" class="story">  
  
  <p>In 2008, Sears adopted an organizational structure that pitted departments against each other. This led to a tribal warfare state of affairs, <a href="https://d3.harvard.edu/platform-rctom/submission/sears-the-collapse-of-a-company-from-within/">accelerating its downfall</a>. Some say that US universities operate somwhat similarly sitll today, with each department reporting its own profit and remaining siloed. While this is slowly changing, I have yet to meet anyone at UVM who understands the broader research ecosystem, particularly around software development. To better understand UVM's research landscape, we take a deep dive into research groups at UVM. We first take a look at the {data.length} UVM faculty, annotated with whether they have a research group or not:</p>
    
    <WaffleChart data={ data } cellSize={25}/>

  <p>We can see that about one third of faculty have research groups, defined here as any claim from faculties to have some kind of research group on the Internet. Now, we can look at how this distribution changes when stratified by:   <span class="grouping-controls">
    <button 
      class:active={groupBy === 'college'}
      onclick={() => groupBy = 'college'}
    >
      Colleges & Schools
    </button>
    <button 
      class:active={groupBy === 'host_dept'}
      onclick={() => groupBy = 'host_dept'}
    >
      Departments
    </button>
  </span>

  </p>

  <div class="waffle-grid">
  {#if groupBy === 'host_dept'}
    <!-- Grouped by college view -->
    {#each groupedData() as [collegeName, departments]}
      <div class="college-section">
        <h3 class="college-header">{collegeName}</h3>
        <div class="department-grid">
          {#each departments as [deptName, deptData]}
            {#if deptName == collegeName}
              <WaffleChart 
                data={deptData} 
                cellSize={20}
              />
              {:else}
              <WaffleChart 
                data={deptData} 
                title="{deptName}"
                cellSize={20}
              />
            {/if}
          {/each}
        </div>
      </div>
    {/each}
  {:else}
    <!-- Regular college view -->
    {#each groupedData() as [groupName, groupData]}
      <WaffleChart 
        data={groupData} 
        title="{groupName}"
        cellSize={25}
      />
    {/each}
  {/if}
</div>


<p>Looking at colleges, we note that roughly a half of faculties in College of Medicine and CEMS have research groups, while the College of Agriculture and Life Sciences (CALS) and the Rubenstein School of Environment is more about two thirds! In the College of Arts and Sciences (CAS), it is fewer than a third, with {(19/80)*100}% of faculties having groups. In the College of Nursing and Health Sciences, Education and Social Services, and Business, faculties with research groups are in the minority, hinting at different epistemic cultures at UVM.</p>  

<p>Looking at department level, we can see that most groups in CAS are either in Psychological Science, Biology, or Chemistry. In CALS, it is also heterogenous with CDAE having no research groups, while in other departments the majority of faculties do have groups.</p>

</section>
  

<style >


  section p {
    font-size: 22px;
    max-width: 800px;
    line-height: 1.3;
    margin-top: 2rem; /* Add more space after paragraphs */
    margin-bottom: 2rem; /* Add more space after paragraphs */
  }


  .waffle-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    margin: 0 0;
  }

  .college-section {
  grid-column: 1 / -1; /* Span full width */
  margin-bottom: 2rem;
}

.college-header {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #ddd;
  color: #333;
}

.department-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}


  /* Story-wide settings */
  :global(#story) {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  :global(#story h1) {
    font-size: var(--font-size-xlarge);
    margin: 2rem 0 3rem 0;
    text-align: left;
    font-family: var(--serif);
  }

  
  .grouping-controls {
  display: inline;
  gap: 0;
  margin: 0;
  justify-content: center;
}

.grouping-controls button {
  padding: 0.5rem 1rem;
  border: 2px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.grouping-controls button:hover {
  border-color: #999;
}

.grouping-controls button.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

  
</style>