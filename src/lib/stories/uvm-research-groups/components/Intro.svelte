<script>
  import WaffleChart from './Waffle.svelte';
  import { group } from 'd3-array'
  import { base } from '$app/paths';

  let { data } = $props();
  
  let groupBy = $state('college'); // 'college' or 'department'
  
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
    
    if (groupBy === 'department') {
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
  
  <p>In 2008, Sears adopted an organizational structure that pitted departments against each other. This led to a tribal warfare state of affairs, <a href="https://d3.harvard.edu/platform-rctom/submission/sears-the-collapse-of-a-company-from-within/">accelerating its downfall</a>. Some say that US universities operate somewhat similarly today, with each department reporting its own profit and remaining siloed. While this is slowly changing, I have yet to meet anyone at UVM who understands the broader research ecosystem, particularly around software development.</p> 
  
  <p>To better understand UVM's research landscape, we take a deep dive into research groups at UVM. We first take a look at the {data.length} UVM faculty (as of 2023, based on <a href="https://www.uvm.edu/d10-files/documents/2024-12/2024-2025-Base-Pay.pdf">payroll</a>):</p>
    
    <WaffleChart {data} cellSize={25} highlightCategory="no_oa_uid"/>

  <p>We denote faculties with or without research groups in yellow and green in typical UVM fashion. Highlighted in red, we have faculties without openAlex identifiers, which we use as our main academic database for authors metadata. As can be seen below, these are mostly faculties engage in the arts; theater, music, dance, art history.</p>
  <p>Last but not least, we chose to represent perceived sex as binary shape. Unfortunately, we didn't record how faculty gender identity, and even if we did we are hesitant to share the data here. The assessment of perceived sex was done while annotating faculties with research groups and not, and was based on perceived information about faculties; mostly their faculty headshot. We felt it was important to represent that category to better understand gendered patterns in science, and in particular at UVM.</p>
  <p>Now, we can see that about one third of faculty have research groups, defined here as any claim from faculties to have some kind of research group on the Internet. This is a somewhat restrictive definition of research groups, which aligned with the idea of groups in collective action theory. That is, it is a definition of groups that stem from individuals, here principal  (PIs), recognizing themselves as such. Now, we can look at how this proportion changes when stratified by  <span class="grouping-controls">
    <button 
      class:active={groupBy === 'college'}
      onclick={() => groupBy = 'college'}
    >
      Colleges & Schools
    </button>
    or
    <button 
      class:active={groupBy === 'department'}
      onclick={() => groupBy = 'department'}
    >
      Departments
    </button>
  </span>

  </p>

  <div class="waffle-grid">
  {#if groupBy === 'department'}
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
                highlightCategory="no_oa_uid"
              />
              {:else}
              <WaffleChart 
                data={deptData} 
                title={deptName}
                cellSize={20}
                highlightCategory="no_oa_uid"
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
        title={groupName}
        cellSize={25}
        highlightCategory="no_oa_uid"
      />
    {/each}
  {/if}
</div>

<p>Already those waffle charts are saying something interesting. Looking at colleges, we note that roughly half of faculties in College of Medicine and CEMS have research groups. Eyeballing perceived sex, there are more male PIs with reseach groups ({(25/30 * 100).toFixed(2)}% of PIs are also males) in the College of Medicine than women (versus {(27/40 * 100).toFixed(2)}% of non-PIs are perceived as males. Combining both numbers, one realize that only {(16/69*100).toFixed(2)}% of faculties in the College of Medicine are women).</p>
<p>CEMS has an even lower proportion with only {3/24*100}% PIs perveid as women. We shold be careful in interpreting those numbers at face value though. Part of our definition of research group is that the faculty is claiming publicly (on the Internet) to have a group. By that definition, <a href="https://drizzo.w3.uvm.edu/">Donna M. Rizzo</a>, for example, has more graduate students than some PIs, but she never explicitly says that this is "her research group". We had to draw the line somewhere. Future modeling work could potentially address those pitfalls, but the <a href="https://arxiv.org/abs/2507.02758">ontology of groups</a> is famously hard to pin down.</p>
  
<p>The the College of Agriculture and Life Sciences (CALS) and the Rubenstein School of Environment have higher proportion of faculties with groups and are closer to gender equality! Finally, as one would expect, the College of Arts and Sciences (CAS) has fewer PIs, with about {(19/80)*100}% of faculties having groups. In the College of Nursing and Health Sciences, Education and Social Services, and Business, faculties with research groups are in the minority, hinting at different epistemic cultures at UVM.</p>  

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