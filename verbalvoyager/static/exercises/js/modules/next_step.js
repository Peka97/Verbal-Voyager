export function toNextStep(current_step) {
    let curr_step_el = document.getElementById(`step_${current_step}`);
    
    curr_step_el.classList.remove('active', 'step-active');
    curr_step_el.classList.add('step-complete');

    let next_step_el = document.getElementById(`step_${current_step + 1}`);
    next_step_el.classList.remove('step-future', 'disabled');
    next_step_el.classList.add('next-btn', 'active');

    document.getElementById(`step_${current_step + 1}`).children[1].classList.remove('disabled'); // stars
    document.getElementById(`step_${current_step + 1}`).children[2].classList.remove('disabled'); // glow
}